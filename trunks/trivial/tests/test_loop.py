# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""The loop of one run, on a clock the test moves (TRV-0, "One loop and one watch", "Stopping the run")."""
import time

from fake_driver import MovedClock, ScriptedDriver, event, finished
from arbol_trunk_trivial.driver import DriverRun
from arbol_trunk_trivial.end import end_of_run


import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from fake_driver import MovedClock, ScriptedDriver, finished
from fakes import FakeDatabase

from arbol_trunk_trivial.control import ControlFile
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
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


STOP = '{"type":"stop"}'


class SilentRuns(LoopTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class StoppingTheRun(LoopTest):
    """TRV-0.11: a stop line on the control input, and SIGKILL for a Driver still alive 16 seconds after it."""

    def end_when_stopped(self, after: float) -> None:
        """The Driver finishes as cancelled and exits `after` seconds after it was handed a stop line."""
        def on_control(line: str) -> None:
            if json.loads(line).get("type") == "stop":
                self.driver.after(after, "event", finished(9, "cancelled"))
                self.driver.after(after + 0.1, "exit", 2)

        self.driver.on_control = on_control


class Answers(LoopTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


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
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
