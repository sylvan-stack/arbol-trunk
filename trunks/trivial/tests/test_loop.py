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
        self.driver = ScriptedDriver(self.clock)
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
        self.driver = ScriptedDriver(self.clock, holds_output=True)
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

            def timed(line: str) -> None:
                began = time.monotonic()
                write(line)
                writes.append(time.monotonic() - began)

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
