"""The loop of one run, on a clock the test moves (TRV-0, "One loop and one watch", "Stopping the run")."""

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
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::Loop.test_the_run_is_over_once_its_process_has_ended_and_its_output_is_read_to_the_end
#     def test_the_run_is_over_once_its_process_has_ended_and_its_output_is_read_to_the_end(self) -> None:
#         self.driver.at(0.5, "event", event(1, "started"))
#         self.driver.at(1.2, "event", finished(2))
#         self.driver.at(1.3, "end_output")
#         self.driver.at(2.4, "exit", 0)
#         over = self.drive()
#         self.assertEqual(over.finished, finished(2))
#         self.assertEqual(self.clock.since_start(), 2.4)
#         self.assertEqual([line["n"] for line in self.lines()], [1, 2])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::Loop.test_the_run_is_over_once_its_process_has_ended_and_its_output_is_read_to_the_end

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::Loop.test_output_kept_open_after_the_exit_is_read_for_one_second_more
#     def test_output_kept_open_after_the_exit_is_read_for_one_second_more(self) -> None:
#         self.driver = ScriptedDriver(self.clock, holds_output=True, control_file=self.folder / "control")
#         self.driver.at(0.2, "event", finished(1))
#         self.driver.at(2.0, "exit", 0)
#         self.driver.at(2.5, "event", event(2, "notice", code="late", message="Still read."))
#         self.driver.at(3.5, "event", event(3, "notice", code="later", message="Not read."))
#         self.drive()
#         self.assertEqual(self.clock.since_start(), 3.0)
#         self.assertEqual([line["event"]["seq"] for line in self.lines()], [1, 2])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::Loop.test_output_kept_open_after_the_exit_is_read_for_one_second_more

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::Loop.test_the_loop_goes_on_in_rounds_of_a_second_until_the_process_ends
#     def test_the_loop_goes_on_in_rounds_of_a_second_until_the_process_ends(self) -> None:
#         self.driver.at(1.0, "end_output")
#         self.driver.at(5.5, "exit", 0)
#         over = self.drive()
#         self.assertIsNone(over.finished)
#         self.assertEqual(self.clock.since_start(), 5.5)
#         self.assertTrue(all(wait <= 1.0 for wait in self.driver.waits))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::Loop.test_the_loop_goes_on_in_rounds_of_a_second_until_the_process_ends

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::Loop.test_the_rounds_are_divided_by_the_time_scale
#     def test_the_rounds_are_divided_by_the_time_scale(self) -> None:
#         os.environ["ARBOL_TEST_TIME_SCALE"] = "10"
#         self.driver.at(1.0, "exit", 0)
#         self.drive()
#         self.assertEqual(max(self.driver.waits), 0.1)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::Loop.test_the_rounds_are_divided_by_the_time_scale


STOP = '{"type":"stop"}'


class SilentRuns(LoopTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::SilentRuns.test_sixteen_minutes_without_a_first_event_uses_the_awake_clock_and_the_scaled_duration
#     def test_sixteen_minutes_without_a_first_event_uses_the_awake_clock_and_the_scaled_duration(self) -> None:
#         for scale, expected in (("1", 960), ("10", 96)):
#             with self.subTest(scale=scale):
#                 self.clock = MovedClock()
#                 self.driver = ScriptedDriver(self.clock)
#                 with mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": scale}):
#                     over = self.drive()
#                 self.assertTrue(over.silent)
#                 self.assertTrue(over.stopped)
#                 self.assertAlmostEqual(self.driver.control[0][0], expected)
#                 self.assertEqual(self.driver.control[0][1], STOP)
#                 self.assertAlmostEqual(self.driver.killed_at or 0, expected + 16 / int(scale))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::SilentRuns.test_sixteen_minutes_without_a_first_event_uses_the_awake_clock_and_the_scaled_duration

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::SilentRuns.test_every_event_resets_silence_even_when_its_tool_output_is_omitted
#     def test_every_event_resets_silence_even_when_its_tool_output_is_omitted(self) -> None:
#         self.events.tool_bytes[("x.1", "c")] = 1024 * 1024 + 1
#         self.driver.at(0, "event", event(1, "started"))
#         self.driver.at(900, "event", event(2, "tool_output_delta", callId="c", text="still alive"))
#         self.driver.at(1859, "event", finished(3))
#         self.driver.at(1860, "exit", 0)
#         over = self.drive()
#         self.assertFalse(over.silent)
#         self.assertEqual(self.driver.control, [])
#         self.assertEqual([line["event"]["type"] for line in self.lines()], ["started", "finished"])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::SilentRuns.test_every_event_resets_silence_even_when_its_tool_output_is_omitted

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::SilentRuns.test_an_open_tool_or_question_can_wait_for_hours_without_counting_as_silence
#     def test_an_open_tool_or_question_can_wait_for_hours_without_counting_as_silence(self) -> None:
#         self.driver.at(0, "event", event(1, "started"))
#         self.driver.at(1, "event", event(2, "tool_started", callId="c", name="shell", input={}))
#         self.driver.at(7201, "event", event(3, "tool_finished", callId="c", ok=True))
#         self.driver.at(7202, "event", event(4, "ask_opened", askId="q", ask={"callId": "a"}))
#         self.driver.at(14402, "event", event(5, "ask_closed", askId="q"))
#         self.driver.at(14403, "event", finished(6))
#         self.driver.at(14404, "exit", 0)
#         over = self.drive()
#         self.assertFalse(over.silent)
#         self.assertEqual(self.driver.control, [])
#         self.assertEqual(self.clock.since_start(), 14404)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::SilentRuns.test_an_open_tool_or_question_can_wait_for_hours_without_counting_as_silence

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::SilentRuns.test_a_mac_asleep_for_an_hour_does_not_add_an_hour_to_silence
#     def test_a_mac_asleep_for_an_hour_does_not_add_an_hour_to_silence(self) -> None:
#         class SleepingDriver(ScriptedDriver):
#             asleep = True
#             wall_sleep = 0
#
#             async def read(self, seconds: float) -> list[Any]:
#                 if self.asleep:
#                     self.asleep = False
#                     self.wall_sleep += 3600  # the test's awake clock stands still for the simulated sleep
#                     return []
#                 return await super().read(seconds)
#
#         driver = SleepingDriver(self.clock)
#         self.driver = driver
#         with mock.patch("time.time", side_effect=lambda: self.clock.now() + driver.wall_sleep):
#             over = self.drive()
#         self.assertTrue(over.silent)
#         self.assertEqual(driver.wall_sleep, 3600)
#         self.assertEqual(driver.control, [(960, STOP)])
#         self.assertEqual(driver.killed_at, 976)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::SilentRuns.test_a_mac_asleep_for_an_hour_does_not_add_an_hour_to_silence


class StoppingTheRun(LoopTest):
    """TRV-0.11: a stop line on the control input, and SIGKILL for a Driver still alive 16 seconds after it."""

    def end_when_stopped(self, after: float) -> None:
        """The Driver finishes as cancelled and exits `after` seconds after it was handed a stop line."""
        def on_control(line: str) -> None:
            if json.loads(line).get("type") == "stop":
                self.driver.after(after, "event", finished(9, "cancelled"))
                self.driver.after(after + 0.1, "exit", 2)

        self.driver.on_control = on_control

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::StoppingTheRun.test_a_driver_that_ends_after_its_stop_line_is_not_killed_and_the_exchange_is_cancelled
#     def test_a_driver_that_ends_after_its_stop_line_is_not_killed_and_the_exchange_is_cancelled(self) -> None:
#         self.driver.at(0.3, "event", event(1, "started"))
#         self.driver.at(0.5, "control", STOP)
#         self.end_when_stopped(2.0)
#         over = self.drive()
#         self.assertEqual(self.driver.control, [(0.5, STOP)])
#         self.assertIsNone(self.driver.killed_at)
#         self.assertEqual(self.clock.since_start(), 2.6)
#         self.assertTrue(over.stopped)
#         self.assertEqual(end_of_run(over.finished, stopped=over.stopped).state, "cancelled")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::StoppingTheRun.test_a_driver_that_ends_after_its_stop_line_is_not_killed_and_the_exchange_is_cancelled

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::StoppingTheRun.test_a_driver_still_alive_16_seconds_after_its_stop_line_is_killed_then_and_not_later
#     def test_a_driver_still_alive_16_seconds_after_its_stop_line_is_killed_then_and_not_later(self) -> None:
#         self.driver.at(0.3, "event", event(1, "started"))
#         self.driver.at(0.5, "control", STOP)
#         over = self.drive()
#         self.assertEqual(self.driver.control, [(0.5, STOP)])
#         self.assertEqual(self.driver.killed_at, 16.5)
#         self.assertEqual(self.clock.since_start(), 16.5)
#         self.assertTrue(all(wait <= 1.0 for wait in self.driver.waits))
#         self.assertIsNone(over.finished)
#         self.assertEqual(end_of_run(over.finished, stopped=over.stopped).state, "cancelled")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::StoppingTheRun.test_a_driver_still_alive_16_seconds_after_its_stop_line_is_killed_then_and_not_later

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::StoppingTheRun.test_the_16_seconds_count_from_the_first_stop_line_and_are_divided_by_the_time_scale
#     def test_the_16_seconds_count_from_the_first_stop_line_and_are_divided_by_the_time_scale(self) -> None:
#         os.environ["ARBOL_TEST_TIME_SCALE"] = "10"
#         self.driver.at(0.05, "control", STOP)
#         self.driver.at(1.0, "control", STOP)
#         self.drive()
#         self.assertEqual([line for _at, line in self.driver.control], [STOP, STOP])
#         self.assertEqual(self.driver.killed_at, 1.65)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::StoppingTheRun.test_the_16_seconds_count_from_the_first_stop_line_and_are_divided_by_the_time_scale

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::StoppingTheRun.test_a_driver_still_alive_16_seconds_after_its_finished_is_killed_and_the_run_keeps_its_outcome
#     def test_a_driver_still_alive_16_seconds_after_its_finished_is_killed_and_the_run_keeps_its_outcome(self) -> None:
#         self.driver.at(0.3, "event", event(1, "started"))
#         self.driver.at(2.0, "event", finished(2, "completed"))
#         over = self.drive()
#         self.assertEqual(self.driver.killed_at, 18.0)
#         self.assertEqual(self.driver.control, [])
#         self.assertEqual(end_of_run(over.finished, stopped=over.stopped).state, "completed")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::StoppingTheRun.test_a_driver_still_alive_16_seconds_after_its_finished_is_killed_and_the_run_keeps_its_outcome

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::StoppingTheRun.test_the_16_seconds_count_from_whichever_came_first
#     def test_the_16_seconds_count_from_whichever_came_first(self) -> None:
#         self.driver.at(2.0, "event", finished(1, "completed"))
#         self.driver.at(10.0, "control", STOP)
#         self.drive()
#         self.assertEqual(self.driver.killed_at, 18.0)
#         self.clock = MovedClock()
#         self.driver = ScriptedDriver(self.clock, control_file=self.folder / "control")
#         self.driver.at(1.0, "control", STOP)
#         self.driver.at(5.0, "event", finished(1, "cancelled"))
#         self.drive()
#         self.assertEqual(self.driver.killed_at, 17.0)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::StoppingTheRun.test_the_16_seconds_count_from_whichever_came_first

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::StoppingTheRun.test_a_full_file_sends_the_same_stop_and_kills_a_driver_that_does_not_end
#     def test_a_full_file_sends_the_same_stop_and_kills_a_driver_that_does_not_end(self) -> None:
#         self.driver.at(0.1, "event", event(1, "started"))
#         self.driver.at(0.5, "event", event(2, "text", text="x" * 2000))
#         with mock.patch("arbol_trunk_trivial.events.FILE_BYTES", 200):
#             self.drive()
#         self.assertTrue(self.events.full)
#         self.assertEqual(self.driver.control, [(0.5, STOP)])
#         self.assertEqual(self.driver.killed_at, 16.5)
#         self.assertEqual([line["event"]["type"] for line in self.lines()], ["started"])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::StoppingTheRun.test_a_full_file_sends_the_same_stop_and_kills_a_driver_that_does_not_end

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::StoppingTheRun.test_a_run_that_completed_before_the_stop_reached_it_keeps_its_outcome
#     def test_a_run_that_completed_before_the_stop_reached_it_keeps_its_outcome(self) -> None:
#         self.driver.at(0.5, "control", STOP)
#         self.driver.at(0.7, "event", finished(1, "completed"))
#         self.driver.at(0.8, "exit", 0)
#         over = self.drive()
#         self.assertEqual(end_of_run(over.finished, stopped=over.stopped).state, "completed")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::StoppingTheRun.test_a_run_that_completed_before_the_stop_reached_it_keeps_its_outcome


class Answers(LoopTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::Answers.test_each_answer_handed_on_is_appended_exactly_as_it_was_in_control
#     def test_each_answer_handed_on_is_appended_exactly_as_it_was_in_control(self) -> None:
#         answer = '{"askId" : "ask_2", "type":"answer",  "answer":{"type":"answers","answers":{"branch":["main"]}}}'
#         self.driver.at(0.2, "event", event(1, "started"))
#         self.driver.at(0.3, "event", event(2, "ask_opened", askId="ask_2", ask={"callId": "call_1", "questions": []}))
#         self.driver.at(0.4, "control", answer)
#         self.driver.at(1.5, "event", event(3, "ask_closed", askId="ask_2", reason="answered"))
#         self.driver.at(1.6, "event", finished(4))
#         self.driver.at(1.7, "exit", 0)
#         self.drive()
#         self.assertEqual([line for _at, line in self.driver.control], [answer])
#         raw = (self.folder / "events.jsonl").read_text().splitlines()
#         self.assertEqual(raw[2], '{"n":3,"answer":' + answer + "}")
#         self.assertEqual([json.loads(line)["n"] for line in raw], [1, 2, 3, 4, 5])
#         self.assertEqual(json.loads(raw[3])["event"]["type"], "ask_closed")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::Answers.test_each_answer_handed_on_is_appended_exactly_as_it_was_in_control

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::Answers.test_an_answer_that_could_not_be_handed_on_is_not_appended
#     def test_an_answer_that_could_not_be_handed_on_is_not_appended(self) -> None:
#         self.driver.write_control = lambda line: False  # type: ignore[method-assign]
#         self.driver.at(0.2, "control", '{"type":"answer","askId":"ask_1","answer":{"type":"decline"}}')
#         self.driver.at(0.5, "exit", 0)
#         self.drive()
#         self.assertEqual(self.lines(), [])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::Answers.test_an_answer_that_could_not_be_handed_on_is_not_appended


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
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_loop.py::HandingOn.test_each_line_goes_unchanged_to_the_control_input_and_what_the_driver_has_not_taken_waits_in_order
#     def test_each_line_goes_unchanged_to_the_control_input_and_what_the_driver_has_not_taken_waits_in_order(
#             self) -> None:
#         lines = ['{"type":"answer","askId":"ask_1","answer":{"type":"answers","answers":{"q":["%s"]}}}' % (str(i) * 60000)
#                  for i in range(2)] + ['{ "type" : "stop" }']
#         for line in lines:
#             append(self.folder / "control", line)
#         launcher = self.folder / "arbol-claude-driver"
#         launcher.write_text(SLOW_READER)
#         os.chmod(launcher, 0o755)
#         (self.folder / "run-1.json").write_text("{}")
#         writes: list[float] = []
#
#         async def go() -> RunOver:
#             run = await DriverRun.start(str(launcher), self.folder / "run-1.json", str(self.folder))
#             write = run.write_control
#
#             def timed(line: str) -> bool:
#                 began = time.monotonic()
#                 handed = write(line)
#                 writes.append(time.monotonic() - began)
#                 return handed
#
#             run.write_control = timed  # type: ignore[method-assign]
#             over = await drive(run, self.events, RowMaker("x"), Saver(FakeDatabase().connect()), self.control)
#             await run.wait()
#             return over
#
#         over = asyncio.run(go())
#         self.assertEqual(over.finished["seq"] if over.finished else None, 2)
#         self.assertEqual((self.folder / "received").read_text(), "".join(line + "\n" for line in lines))
#         self.assertEqual(len(writes), 3)
#         self.assertLess(max(writes), 0.05)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_loop.py::HandingOn.test_each_line_goes_unchanged_to_the_control_input_and_what_the_driver_has_not_taken_waits_in_order


if __name__ == "__main__":
    unittest.main()

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_loop.py:7
# import time
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_loop.py:7
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_loop.py:13
# from fake_driver import MovedClock, ScriptedDriver, event, finished
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_loop.py:13
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_loop.py:17
# from arbol_trunk_trivial.driver import DriverRun
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_loop.py:17
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_loop.py:18
# from arbol_trunk_trivial.end import end_of_run
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_loop.py:18
