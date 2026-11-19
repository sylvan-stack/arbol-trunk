"""Run an Exchange through durable acceptance, Steady's phases, and persistence of the end (STE-0)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import phases
from .accept import Exchange, Repeated, accept_message
from .clock import UPTIME, Clock, scaled
from .control import ControlFile
from .database import Connect, writer_connections
from .detach import detach
from .driver import CapabilityError, CapabilityStopped, Driver, DriverRun, capabilities, find_launcher, launcher_name
from .end import End, cancelled, end_of_run, failed, save_end, write_end
from .errors import Refusal
from .events import EventsFile
from .life import SignsOfLife
from .output import Output as Output
from .request import run_request, write_request
from .rows import RowMaker
from .saver import Saver
from .start import Prepared
from .watch import Watch

ROUND_SECONDS = 1.0
OUTPUT_AFTER_EXIT_SECONDS = 1.0
SILENCE_SECONDS = 16 * 60.0
STOP_SECONDS = 16.0  # from the stop line, or the run's finished, to SIGKILL; a Driver has 15 for a stop (TRV-D8)


async def run_exchange(prepared: Prepared, connect: Connect, *, build: str, process: dict[str, Any],
                       started: float, output: Output | None = None, search_path: str | None = None) -> int:
    """Accepts the message, says so on standard output, and runs the Exchange to its end. The exit status is 0 for
    completed, 1 for failed or refused, 2 for cancelled (RCT-2)."""
    async with writer_connections(connect) as connect:
        output = output or Output()
        life = SignsOfLife()
        watch = Watch(life)
        watch.start()
        try:
            try:
                exchange = await life.wait(accept_message(prepared, connect, build=build, process=process,
                                                           started=started), "database")
            except Repeated as repeated:
                output.line(repeated.line)
                return 0
            except Refusal as refusal:
                output.line(refusal.line())
                return 1
            life.bind(exchange.folder)
            life.beat("database")
            output.line(exchange.line)
            if prepared.handed.detach:
                detach()
                output.broken = True
            end = await run_accepted(prepared, connect, exchange, search_path, output, life=life)
            return end.exit_status
        finally:
            watch.close()


async def run_accepted(prepared: Prepared, connect: Connect, exchange: Exchange, search_path: str | None,
                       output: Output | None = None, *, life: SignsOfLife | None = None) -> End:
    folder = exchange.folder
    life = life or SignsOfLife(folder)
    events = EventsFile(folder.path / "events.jsonl", output)
    maker = RowMaker(folder.exchange)
    saver = Saver(connect, exchange.connection)
    saver.start()

    async def execute(data: phases.ExchangeData) -> End:
        return await execution(prepared, exchange, events, maker, saver, search_path, life, data)

    try:
        try:
            earlier_messages = [
                item["text"] for item in exchange.history
                if item.get("type") == "message" and item.get("role") == "user" and isinstance(item.get("text"), str)
            ]
            end = await phases.intake(prepared.installation.home, folder.path, exchange.message,
                                      earlier_messages, execute)
        except OSError as error:
            life.error = error
            end = folder_failed(error)
        except Exception as error:  # a defect of the Trunk still ends the Exchange (RCT-2.9)
            end = failed("trunk_failed", f"The Trunk failed: {type(error).__name__}: {error}")
        await saver.stop()
        if saver.rejected is not None and events.error is None and life.error is None:
            end = failed("trunk_failed", str(saver.rejected))
        end = phases.finalization(end)
        try:
            if events.error is None and life.error is None:
                if events.end_fills(end.value()):
                    end = file_full()
                write_end(events, folder, end)
        except OSError as error:
            life.error = error
            end = folder_failed(error)
        events.close()
        life.error = life.error or events.error
        saved = await life.wait(save_end(saver, folder.exchange, maker.at_end(), end), "database")
        if saved and events.error is None and life.error is None:
            try:
                folder.remove()
            except OSError:
                pass  # the end already stands; settling can remove what cleanup left
        return end
    finally:
        events.close()
        await saver.close()


def file_full() -> End:
    return failed("events_file_full", "The Exchange's events file reached its 256 MiB limit.")


def folder_failed(error: OSError | None) -> End:
    return failed("folder_unwritable", f"The Exchange's folder cannot be written: {error}.")


async def execution(prepared: Prepared, exchange: Exchange, events: EventsFile, maker: RowMaker, saver: Saver,
                    search_path: str | None, life: SignsOfLife, data: phases.ExchangeData) -> End:
    """Run the selected Driver once and return the Exchange outcome."""
    if events.error is not None or life.error is not None:
        return folder_failed(events.error or life.error)
    folder = exchange.folder
    launcher = find_launcher(prepared.driver, search_path)
    if launcher is None:
        return failed("driver_failed", f"No folder of the search path holds the launcher "
                                       f"{launcher_name(prepared.driver)}.")
    control = ControlFile(folder.path / "control")
    try:
        if any(line.kind == "stop" for line in control.read()):  # read just before the run (RCT-2.7, TRV-0.1)
            return cancelled()
        try:
            accepts_cue_context = await life.wait(
                capabilities(launcher, prepared.driver, prepared.handed.route.get("subscription"),
                             prepared.handed.working_folder, prepared.installation.home,
                             lambda: any(line.kind == "stop" for line in control.read())), "driver")
        except CapabilityStopped:
            return cancelled()
        except CapabilityError as error:
            return failed("driver_failed", str(error))
        except OSError as error:
            return failed("driver_failed", f"The launcher {launcher} could not be started: {error.strerror}.")
        if life.error is not None:
            return folder_failed(life.error)
        request = run_request(exchange=folder.exchange, chat=exchange.chat, driver=prepared.driver,
                              route=prepared.handed.route, working_folder=prepared.handed.working_folder,
                              history=exchange.history, message=exchange.message,
                              cue_context=data.cue_context if accepts_cue_context else None)
        request_file = write_request(folder.path, request)
        if any(line.kind == "stop" for line in control.read()):
            return cancelled()
        try:
            run = await life.wait(DriverRun.start(launcher, request_file, prepared.handed.working_folder), "driver")
        except OSError as error:
            return failed("driver_failed", f"The launcher {launcher} could not be started: {error.strerror}.")
        over = await drive(run, events, maker, saver, control, life=life)
        run.close_control()
        await run.wait()  # the process has ended; this waits for no pipe (gh-119710)
    finally:
        control.close()
    if events.error is not None or life.error is not None:
        return folder_failed(events.error or life.error)
    if events.full:
        return file_full()
    if over.silent:
        return failed("driver_silent", "The Driver gave no event for 16 minutes with no tool call or question open.")
    if saver.rejected is not None:
        return failed("trunk_failed", str(saver.rejected))
    if over.finished is None and not over.stopped and run.refusal is not None:
        return failed("driver_failed", run.refusal)
    return end_of_run(over.finished, stopped=over.stopped)


@dataclass(frozen=True)
class RunOver:
    """What the loop knew when the run was over: the run's `finished` event, when it came, and whether a stop line was
    handed to it."""

    finished: dict[str, Any] | None
    stopped: bool = False
    silent: bool = False


async def drive(run: Driver, events: EventsFile, maker: RowMaker, saver: Saver, control: ControlFile | None = None,
                clock: Clock = UPTIME, life: SignsOfLife | None = None) -> RunOver:
    """The rounds of the loop for one run, until the run is over: its Driver's process has ended and its output has
    been read to the end, for at most one second after the process ended (TRV-0, "Stopping the run"). Each round waits
    at most one second for output, appends what arrived, and hands each new `stop` and `answer` line of `control`
    unchanged to the run's control input, without waiting for the Driver to take it (RCT-1.7); an answer handed on is
    appended to `events.jsonl` (RCT-1.11). A Driver still alive
    16 seconds after the first stop line it was handed, or after its `finished` when that came first, is ended with
    SIGKILL; each round checks that time and waits past it for nothing (TRV-D8)."""
    finished: dict[str, Any] | None = None
    exited_at: float | None = None
    stopped_at: float | None = None
    finished_at: float | None = None
    killed = False
    last_event = clock.now()
    silent = False
    life = life or SignsOfLife(clock=clock)

    def idle_time() -> float | None:
        if life.tools or life.questions or finished_at is not None or stopped_at is not None:
            return None
        return last_event + scaled(SILENCE_SECONDS)

    def kill_time() -> float | None:
        first = min((at for at in (stopped_at, finished_at) if at is not None), default=None)
        return None if killed or first is None else first + scaled(STOP_SECONDS)

    while True:
        wait = scaled(ROUND_SECONDS)
        if exited_at is not None:
            wait = min(wait, max(exited_at + scaled(OUTPUT_AFTER_EXIT_SECONDS) - clock.now(), 0.0))
        idle_at = idle_time()
        if idle_at is not None and run.returncode is None:
            wait = min(wait, max(idle_at - clock.now(), 0.0))
        kill_at = kill_time()
        if kill_at is not None and run.returncode is None:
            wait = min(wait, max(kill_at - clock.now(), 0.0))
        for line in await run.read(wait):
            last_event = clock.now()  # even an output fragment omitted by a size limit is an event
            try:
                n = events.append_event(line)
            except OSError:
                n = events.append_event(line)  # the failed file is abandoned; retain this line for its rows
            if n is not None:
                saver.add(maker.take(n, line.event))
            life.observe(line.event)
            if line.event.get("type") == "finished" and finished is None:
                finished, finished_at = line.event, clock.now()
        try:
            handed_lines = control.read() if control is not None else []
        except OSError as error:
            events.error = error
            handed_lines = []
        for handed in handed_lines:
            if not run.write_control(handed.text):
                continue
            if handed.kind == "answer":
                try:
                    answer_n = events.append_answer(handed.text)
                except OSError:
                    answer_n = events.append_answer(handed.text)
                if answer_n is not None:
                    saver.add(maker.take_answer(handed.value))
            elif stopped_at is None:
                stopped_at = clock.now()
        life.error = life.error or events.error
        life.beat(life.waiting(driver=True))
        idle_at = idle_time()
        if idle_at is not None and run.returncode is None and clock.now() >= idle_at:
            silent = True
        if stopped_at is None and (events.error is not None or events.full or saver.rejected is not None
                                   or life.error is not None or silent):
            run.write_control('{"type":"stop"}')
            stopped_at = clock.now()
        kill_at = kill_time()
        if kill_at is not None and run.returncode is None and clock.now() >= kill_at:
            run.kill()
            killed = True
        if run.returncode is not None:
            if run.output_ended:
                break
            exited_at = clock.now() if exited_at is None else exited_at
            if clock.now() >= exited_at + scaled(OUTPUT_AFTER_EXIT_SECONDS):
                break
    return RunOver(finished, stopped_at is not None, silent)
