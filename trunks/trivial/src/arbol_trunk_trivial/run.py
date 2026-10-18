"""`run`: one Exchange from the message to its end (TRV-0, "One Exchange, one run").

1. It accepts the message as RCT-2 says, reading the history in the same transaction.
2. It writes the request of the run, `run-1.json`, into the Exchange's folder.
3. It starts the Driver through its launcher, as `run` with a control input and the request file.
4. It hands every event of the run to `events.jsonl` and, through the saving task, to the chat tables.
5. When the run is over, it ends the Exchange with the run's outcome.

The work is one loop in one thread (TRV-D9): each round waits at most one second (divided by ARBOL_TEST_TIME_SCALE) for
output of the Driver, appends what arrived, and comes round again. The run is over when the Driver's process has ended
and its output has been read to the end, for at most one second after the process ended.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .accept import Exchange, accept_message
from .clock import UPTIME, Clock, scaled
from .control import ControlFile
from .database import Connect
from .detach import detach
from .driver import Driver, DriverRun, find_launcher, launcher_name
from .end import End, end_of_run, failed, finish, write_end
from .errors import Refusal
from .events import EventsFile
from .request import run_request, write_request
from .rows import RowMaker
from .saver import Saver
from .start import Prepared

ROUND_SECONDS = 1.0
OUTPUT_AFTER_EXIT_SECONDS = 1.0


class Output:
    """Standard output, which never holds up, changes or ends the Exchange (RCT-2.19): a write that fails ends
    nothing, and nothing more is written there after it."""

    def __init__(self, write: Callable[[str], None] | None = None) -> None:
        self._write = write or _stdout
        self.broken = False

    def line(self, text: str) -> None:
        if self.broken:
            return
        try:
            self._write(text)
        except (OSError, ValueError):
            self.broken = True


def _stdout(text: str) -> None:
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


async def run_exchange(prepared: Prepared, connect: Connect, *, build: str, process: dict[str, Any],
                       started: float, output: Output | None = None, search_path: str | None = None) -> int:
    """Accepts the message, says so on standard output, and runs the Exchange to its end. The exit status is 0 for
    completed, 1 for failed or refused, 2 for cancelled (RCT-2)."""
    output = output or Output()
    try:
        exchange = await accept_message(prepared, connect, build=build, process=process, started=started)
    except Refusal as refusal:
        output.line(refusal.line())
        return 1
    output.line(exchange.line)
    if prepared.handed.detach:
        detach()
        output.broken = True
    end = await run_accepted(prepared, connect, exchange, search_path)
    return end.exit_status


async def run_accepted(prepared: Prepared, connect: Connect, exchange: Exchange, search_path: str | None) -> End:
    folder = exchange.folder
    events = EventsFile(folder.path / "events.jsonl")
    maker = RowMaker(folder.exchange)
    saver = Saver(connect, exchange.connection)
    saver.start()
    try:
        end = await one_run(prepared, exchange, events, maker, saver, search_path)
    except Exception as error:  # a defect of the Trunk still ends the Exchange (RCT-2.9)
        end = failed("trunk_failed", f"The Trunk failed: {type(error).__name__}: {error}")
    try:
        write_end(events, folder, end)
    finally:
        events.close()
    await finish(saver, folder, maker.at_end(), end)
    return end


async def one_run(prepared: Prepared, exchange: Exchange, events: EventsFile, maker: RowMaker, saver: Saver,
                  search_path: str | None) -> End:
    folder = exchange.folder
    launcher = find_launcher(prepared.driver, search_path)
    if launcher is None:
        return failed("driver_failed", f"No folder of the search path holds the launcher "
                                       f"{launcher_name(prepared.driver)}.")
    request = run_request(exchange=folder.exchange, chat=exchange.chat, route=prepared.handed.route,
                          working_folder=prepared.handed.working_folder, history=exchange.history,
                          message=exchange.message)
    request_file = write_request(folder.path, request)
    control = ControlFile(folder.path / "control")
    try:
        try:
            run = await DriverRun.start(launcher, request_file, prepared.handed.working_folder)
        except OSError as error:
            return failed("driver_failed", f"The launcher {launcher} could not be started: {error.strerror}.")
        over = await drive(run, events, maker, saver, control)
        run.close_control()
        await run.wait()  # the process has ended; this waits for no pipe (gh-119710)
    finally:
        control.close()
    return end_of_run(over.finished)


@dataclass(frozen=True)
class RunOver:
    """What the loop knew when the run was over: the run's `finished` event, when it came."""

    finished: dict[str, Any] | None


async def drive(run: Driver, events: EventsFile, maker: RowMaker, saver: Saver, control: ControlFile | None = None,
                clock: Clock = UPTIME) -> RunOver:
    """The rounds of the loop for one run, until the run is over: its Driver's process has ended and its output has
    been read to the end, for at most one second after the process ended (TRV-0, "Stopping the run"). Each round waits
    at most one second for output, appends what arrived, and hands each new `stop` and `answer` line of `control`
    unchanged to the run's control input, without waiting for the Driver to take it (RCT-1.7)."""
    finished: dict[str, Any] | None = None
    exited_at: float | None = None
    while True:
        wait = scaled(ROUND_SECONDS)
        if exited_at is not None:
            wait = min(wait, max(exited_at + scaled(OUTPUT_AFTER_EXIT_SECONDS) - clock.now(), 0.0))
        for line in await run.read(wait):
            n = events.append_event(line)
            saver.add(maker.take(n, line.event))
            if line.event.get("type") == "finished" and finished is None:
                finished = line.event
        for handed in control.read() if control is not None else []:
            run.write_control(handed.text)
        if run.returncode is not None:
            if run.output_ended:
                break
            exited_at = clock.now() if exited_at is None else exited_at
            if clock.now() >= exited_at + scaled(OUTPUT_AFTER_EXIT_SECONDS):
                break
    return RunOver(finished)
