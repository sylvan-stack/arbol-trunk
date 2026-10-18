"""The loop of one run, on a clock the test moves (TRV-0, "One loop and one watch", "Stopping the run")."""

import asyncio
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from fake_driver import MovedClock, ScriptedDriver, event, finished
from fakes import FakeDatabase

from arbol_trunk_trivial.control import ControlFile
from arbol_trunk_trivial.driver import DriverRun
from arbol_trunk_trivial.end import end_of_run
from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.rows import RowMaker
from arbol_trunk_trivial.run import RunOver, drive
from arbol_trunk_trivial.saver import Saver


class LoopTest(unittest.TestCase):
    """A folder with `events.jsonl` and `control`, a clock the test moves and a Driver run that plays on it."""

    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        (self.folder / "events.jsonl").write_bytes(b"")
        self.events = EventsFile(self.folder / "events.jsonl")
        self.addCleanup(self.events.close)
        (self.folder / "control").write_bytes(b"")
        self.control = ControlFile(self.folder / "control")
        self.addCleanup(self.control.close)
        self.clock = MovedClock()
        self.driver = ScriptedDriver(self.clock, control_file=self.folder / "control")
        environment = mock.patch.dict("os.environ")
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop("ARBOL_TEST_TIME_SCALE", None)

    def drive(self) -> RunOver:
        async def go() -> RunOver:
            saver = Saver(FakeDatabase().connect())
            return await drive(self.driver, self.events, RowMaker("x"), saver, self.control, clock=self.clock)

        return asyncio.run(go())

    def lines(self) -> list[dict[str, Any]]:
        return [json.loads(line) for line in (self.folder / "events.jsonl").read_text().splitlines()]


class Loop(LoopTest):
    def test_the_run_is_over_once_its_process_has_ended_and_its_output_is_read_to_the_end(self) -> None:
        self.driver.at(0.5, "event", event(1, "started"))
        self.driver.at(1.2, "event", finished(2))
        self.driver.at(1.3, "end_output")
        self.driver.at(2.4, "exit", 0)
        over = self.drive()
        self.assertEqual(over.finished, finished(2))
        self.assertEqual(self.clock.since_start(), 2.4)
        self.assertEqual([line["n"] for line in self.lines()], [1, 2])

    def test_output_kept_open_after_the_exit_is_read_for_one_second_more(self) -> None:
        self.driver = ScriptedDriver(self.clock, holds_output=True, control_file=self.folder / "control")
        self.driver.at(0.2, "event", finished(1))
        self.driver.at(2.0, "exit", 0)
        self.driver.at(2.5, "event", event(2, "notice", code="late", message="Still read."))
        self.driver.at(3.5, "event", event(3, "notice", code="later", message="Not read."))
        self.drive()
        self.assertEqual(self.clock.since_start(), 3.0)
        self.assertEqual([line["event"]["seq"] for line in self.lines()], [1, 2])

    def test_the_loop_goes_on_in_rounds_of_a_second_until_the_process_ends(self) -> None:
        self.driver.at(1.0, "end_output")
        self.driver.at(5.5, "exit", 0)
        over = self.drive()
        self.assertIsNone(over.finished)
        self.assertEqual(self.clock.since_start(), 5.5)
        self.assertTrue(all(wait <= 1.0 for wait in self.driver.waits))

    def test_the_rounds_are_divided_by_the_time_scale(self) -> None:
        os.environ["ARBOL_TEST_TIME_SCALE"] = "10"
        self.driver.at(1.0, "exit", 0)
        self.drive()
        self.assertEqual(max(self.driver.waits), 0.1)


STOP = '{"type":"stop"}'


class StoppingTheRun(LoopTest):
    """TRV-0.11: a stop line on the control input, and SIGKILL for a Driver still alive 16 seconds after it."""

    def end_when_stopped(self, after: float) -> None:
        """The Driver finishes as cancelled and exits `after` seconds after it was handed a stop line."""
        def on_control(line: str) -> None:
            if json.loads(line).get("type") == "stop":
                self.driver.after(after, "event", finished(9, "cancelled"))
                self.driver.after(after + 0.1, "exit", 2)

        self.driver.on_control = on_control

    def test_a_driver_that_ends_after_its_stop_line_is_not_killed_and_the_exchange_is_cancelled(self) -> None:
        self.driver.at(0.3, "event", event(1, "started"))
        self.driver.at(0.5, "control", STOP)
        self.end_when_stopped(2.0)
        over = self.drive()
        self.assertEqual(self.driver.control, [(0.5, STOP)])
        self.assertIsNone(self.driver.killed_at)
        self.assertEqual(self.clock.since_start(), 2.6)
        self.assertTrue(over.stopped)
        self.assertEqual(end_of_run(over.finished, stopped=over.stopped).state, "cancelled")

    def test_a_driver_still_alive_16_seconds_after_its_stop_line_is_killed_then_and_not_later(self) -> None:
        self.driver.at(0.3, "event", event(1, "started"))
        self.driver.at(0.5, "control", STOP)
        over = self.drive()
        self.assertEqual(self.driver.control, [(0.5, STOP)])
        self.assertEqual(self.driver.killed_at, 16.5)
        self.assertEqual(self.clock.since_start(), 16.5)
        self.assertTrue(all(wait <= 1.0 for wait in self.driver.waits))
        self.assertIsNone(over.finished)
        self.assertEqual(end_of_run(over.finished, stopped=over.stopped).state, "cancelled")

    def test_the_16_seconds_count_from_the_first_stop_line_and_are_divided_by_the_time_scale(self) -> None:
        os.environ["ARBOL_TEST_TIME_SCALE"] = "10"
        self.driver.at(0.05, "control", STOP)
        self.driver.at(1.0, "control", STOP)
        self.drive()
        self.assertEqual([line for _at, line in self.driver.control], [STOP, STOP])
        self.assertEqual(self.driver.killed_at, 1.65)

    def test_a_driver_still_alive_16_seconds_after_its_finished_is_killed_and_the_run_keeps_its_outcome(self) -> None:
        self.driver.at(0.3, "event", event(1, "started"))
        self.driver.at(2.0, "event", finished(2, "completed"))
        over = self.drive()
        self.assertEqual(self.driver.killed_at, 18.0)
        self.assertEqual(self.driver.control, [])
        self.assertEqual(end_of_run(over.finished, stopped=over.stopped).state, "completed")

    def test_the_16_seconds_count_from_whichever_came_first(self) -> None:
        self.driver.at(2.0, "event", finished(1, "completed"))
        self.driver.at(10.0, "control", STOP)
        self.drive()
        self.assertEqual(self.driver.killed_at, 18.0)
        self.clock = MovedClock()
        self.driver = ScriptedDriver(self.clock, control_file=self.folder / "control")
        self.driver.at(1.0, "control", STOP)
        self.driver.at(5.0, "event", finished(1, "cancelled"))
        self.drive()
        self.assertEqual(self.driver.killed_at, 17.0)

    def test_a_run_that_completed_before_the_stop_reached_it_keeps_its_outcome(self) -> None:
        self.driver.at(0.5, "control", STOP)
        self.driver.at(0.7, "event", finished(1, "completed"))
        self.driver.at(0.8, "exit", 0)
        over = self.drive()
        self.assertEqual(end_of_run(over.finished, stopped=over.stopped).state, "completed")


class Answers(LoopTest):
    def test_each_answer_handed_on_is_appended_exactly_as_it_was_in_control(self) -> None:
        answer = '{"askId" : "ask_2", "type":"answer",  "answer":{"type":"answers","answers":{"branch":["main"]}}}'
        self.driver.at(0.2, "event", event(1, "started"))
        self.driver.at(0.3, "event", event(2, "ask_opened", askId="ask_2", ask={"callId": "call_1", "questions": []}))
        self.driver.at(0.4, "control", answer)
        self.driver.at(1.5, "event", event(3, "ask_closed", askId="ask_2", reason="answered"))
        self.driver.at(1.6, "event", finished(4))
        self.driver.at(1.7, "exit", 0)
        self.drive()
        self.assertEqual([line for _at, line in self.driver.control], [answer])
        raw = (self.folder / "events.jsonl").read_text().splitlines()
        self.assertEqual(raw[2], '{"n":3,"answer":' + answer + "}")
        self.assertEqual([json.loads(line)["n"] for line in raw], [1, 2, 3, 4, 5])
        self.assertEqual(json.loads(raw[3])["event"]["type"], "ask_closed")

    def test_an_answer_that_could_not_be_handed_on_is_not_appended(self) -> None:
        self.driver.write_control = lambda line: False  # type: ignore[method-assign]
        self.driver.at(0.2, "control", '{"type":"answer","askId":"ask_1","answer":{"type":"decline"}}')
        self.driver.at(0.5, "exit", 0)
        self.drive()
        self.assertEqual(self.lines(), [])


def append(path: Path, line: str) -> None:
    """One line appended with one write, as a writer of `control` appends it (RCT-1.8)."""
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
    try:
        os.write(descriptor, line.encode() + b"\n")
    finally:
        os.close(descriptor)


# A launcher that writes its started event, takes no control line for a second, then reads three lines of its control
# input into `received` and finishes.
SLOW_READER = """#!/bin/sh
printf '%s\\n' '{"runId":"x.1","seq":1,"type":"started"}'
sleep 1
head -n 3 > "$(dirname "$0")/received"
printf '%s\\n' '{"runId":"x.1","seq":2,"type":"finished","outcome":"completed","producedOutput":false,"unfinishedCalls":[]}'
"""


class HandingOn(LoopTest):
    def test_each_line_goes_unchanged_to_the_control_input_and_what_the_driver_has_not_taken_waits_in_order(
            self) -> None:
        lines = ['{"type":"answer","askId":"ask_1","answer":{"type":"answers","answers":{"q":["%s"]}}}' % (str(i) * 60000)
                 for i in range(2)] + ['{ "type" : "stop" }']
        for line in lines:
            append(self.folder / "control", line)
        launcher = self.folder / "arbol-claude-driver"
        launcher.write_text(SLOW_READER)
        os.chmod(launcher, 0o755)
        (self.folder / "run-1.json").write_text("{}")
        writes: list[float] = []

        async def go() -> RunOver:
            run = await DriverRun.start(str(launcher), self.folder / "run-1.json", str(self.folder))
            write = run.write_control

            def timed(line: str) -> bool:
                began = time.monotonic()
                handed = write(line)
                writes.append(time.monotonic() - began)
                return handed

            run.write_control = timed  # type: ignore[method-assign]
            over = await drive(run, self.events, RowMaker("x"), Saver(FakeDatabase().connect()), self.control)
            await run.wait()
            return over

        over = asyncio.run(go())
        self.assertEqual(over.finished["seq"] if over.finished else None, 2)
        self.assertEqual((self.folder / "received").read_text(), "".join(line + "\n" for line in lines))
        self.assertEqual(len(writes), 3)
        self.assertLess(max(writes), 0.05)


if __name__ == "__main__":
    unittest.main()
