"""The loop of one run, on a clock the test moves (TRV-0, "One loop and one watch", "Stopping the run")."""

import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from fake_driver import MovedClock, ScriptedDriver, event, finished
from fakes import FakeDatabase

from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.rows import RowMaker
from arbol_trunk_trivial.run import RunOver, drive
from arbol_trunk_trivial.saver import Saver


class Loop(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        (self.folder / "events.jsonl").write_bytes(b"")
        self.events = EventsFile(self.folder / "events.jsonl")
        self.addCleanup(self.events.close)
        self.clock = MovedClock()
        self.driver = ScriptedDriver(self.clock)
        environment = mock.patch.dict("os.environ")
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop("ARBOL_TEST_TIME_SCALE", None)

    def drive(self) -> RunOver:
        async def go() -> RunOver:
            saver = Saver(FakeDatabase().connect())
            return await drive(self.driver, self.events, RowMaker("x"), saver, self.clock)

        return asyncio.run(go())

    def lines(self) -> list[dict[str, Any]]:
        return [json.loads(line) for line in (self.folder / "events.jsonl").read_text().splitlines()]

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


if __name__ == "__main__":
    unittest.main()
