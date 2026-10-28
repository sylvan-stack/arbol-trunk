import os
import tempfile
import unittest
from pathlib import Path

from fake_driver import MovedClock

from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.life import SignsOfLife

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
AT = "2026-10-26T11:00:00.000Z"


class LifeHome(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.exchanges = Path(temporary.name)
        self.folder = ExchangeFolder.make(self.exchanges, X, {
            "exchange": X, "process": {"pid": os.getpid(), "startedAt": AT},
            "signsOfLife": {"heartbeat": 0, "waitingFor": "database", "since": AT}})
        self.clock = MovedClock()
        self.life = SignsOfLife(self.folder, self.clock)


class Heartbeat(LifeHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_life.py::Heartbeat.test_only_the_work_raises_the_counter_and_publishes_its_awake_time
#     def test_only_the_work_raises_the_counter_and_publishes_its_awake_time(self) -> None:
#         before = (self.folder.path / "record.json").read_bytes()
#         self.clock.t += 59
#         self.assertEqual(self.life.heartbeat, 0)
#         self.assertEqual(self.life.last_raised, self.clock.start)
#         self.assertEqual((self.folder.path / "record.json").read_bytes(), before)
#         for n in range(1, 4):
#             self.life.beat()
#             record = json.loads((self.folder.path / "record.json").read_text())
#             self.assertEqual(record, {**self.folder.record, "signsOfLife": {
#                 "heartbeat": n, "waitingFor": "database", "since": AT}})
#             self.assertEqual(self.life.last_raised, self.clock.t)
#             self.clock.t += 1
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_life.py::Heartbeat.test_only_the_work_raises_the_counter_and_publishes_its_awake_time

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_life.py::Heartbeat.test_a_raise_replaces_the_record_whole_and_preserves_its_other_fields
#     def test_a_raise_replaces_the_record_whole_and_preserves_its_other_fields(self) -> None:
#         with (self.folder.path / "record.json").open("rb") as reader:
#             before = reader.read()
#             self.life.beat()
#             reader.seek(0)
#             self.assertEqual(reader.read(), before)
#         self.assertEqual(self.folder.record["exchange"], X)
#         self.assertEqual(sorted(p.name for p in self.folder.path.iterdir()), ["control", "events.jsonl", "record.json"])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_life.py::Heartbeat.test_a_raise_replaces_the_record_whole_and_preserves_its_other_fields

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_life.py::Heartbeat.test_a_watch_can_exist_before_the_exchange_has_a_folder
#     def test_a_watch_can_exist_before_the_exchange_has_a_folder(self) -> None:
#         life = SignsOfLife(clock=self.clock)
#         life.bind(self.folder)
#         life.beat()
#         self.assertEqual(life.heartbeat, 1)
#         self.assertEqual(self.folder.record["signsOfLife"]["heartbeat"], 1)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_life.py::Heartbeat.test_a_watch_can_exist_before_the_exchange_has_a_folder


class Waiting(LifeHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_life.py::Waiting.test_the_first_true_wait_in_the_contracts_order_wins
#     def test_the_first_true_wait_in_the_contracts_order_wins(self) -> None:
#         cases = [({}, "database"), ({"small_call": True}, "small-call"), ({"driver": True}, "driver"),
#                  ({"tool": True}, "tool"), ({"answer": True}, "answer"),
#                  ({"driver": True, "small_call": True}, "driver"),
#                  ({"tool": True, "driver": True, "small_call": True}, "tool"),
#                  ({"answer": True, "tool": True, "driver": True, "small_call": True}, "answer")]
#         for flags, expected in cases:
#             with self.subTest(flags=flags):
#                 self.assertEqual(waiting_for(**flags), expected)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_life.py::Waiting.test_the_first_true_wait_in_the_contracts_order_wins

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_life.py::Waiting.test_since_changes_only_when_the_wait_changes
#     def test_since_changes_only_when_the_wait_changes(self) -> None:
#         with mock.patch("arbol_trunk_trivial.life.iso", return_value="2026-10-26T11:01:00.000Z"):
#             self.life.beat("driver")
#         with mock.patch("arbol_trunk_trivial.life.iso", return_value="2026-10-26T11:02:00.000Z"):
#             self.life.beat("driver")
#             self.assertEqual(self.folder.record["signsOfLife"]["since"], "2026-10-26T11:01:00.000Z")
#             self.life.beat("tool")
#         self.assertEqual(self.folder.record["signsOfLife"], {
#             "heartbeat": 3, "waitingFor": "tool", "since": "2026-10-26T11:02:00.000Z"})
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_life.py::Waiting.test_since_changes_only_when_the_wait_changes

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_life.py::Waiting.test_questions_and_calls_follow_their_events_until_they_close
#     def test_questions_and_calls_follow_their_events_until_they_close(self) -> None:
#         events = [
#             ({"type": "tool_started", "callId": "call"}, "tool"),
#             ({"type": "ask_opened", "askId": "question"}, "answer"),
#             ({"type": "text", "text": "still waiting"}, "answer"),
#             ({"type": "ask_closed", "askId": "question"}, "tool"),
#             ({"type": "tool_finished", "callId": "call"}, "driver"),
#             ({"type": "tool_started", "callId": "cut-off"}, "tool"),
#             ({"type": "finished"}, "driver")]
#         for event, expected in events:
#             self.life.observe({"runId": "run", **event})
#             self.assertEqual(self.life.waiting(driver=True), expected)
#         self.assertEqual(self.life.waiting(), "database")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_life.py::Waiting.test_questions_and_calls_follow_their_events_until_they_close


class RoundsWithLife(LifeHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_life.py::RoundsWithLife.test_a_database_save_that_never_answers_holds_up_no_round_or_raise
#     def test_a_database_save_that_never_answers_holds_up_no_round_or_raise(self) -> None:
#         clock = self.clock
#
#         class YieldingDriver(ScriptedDriver):
#             async def read(self, seconds: float) -> list[Line]:
#                 await asyncio.sleep(0)
#                 return await super().read(seconds)
#
#         async def work() -> None:
#             entered = asyncio.Event()
#
#             async def slow(connection: FakeConnection, row: Row) -> None:
#                 entered.set()
#                 await asyncio.Future[None]()
#
#             driver = YieldingDriver(clock)
#             driver.at(0, "event", {"runId": "run", "type": "text", "text": "save this"})
#             driver.at(30, "event", {"runId": "run", "type": "finished", "outcome": "completed"})
#             driver.at(30, "exit", 0)
#             database = FakeDatabase()
#             saver = Saver(database.connect())
#             events = EventsFile(self.folder.path / "events.jsonl")
#             saver.start()
#             try:
#                 with mock.patch.object(FakeConnection, "save", slow):
#                     await drive(driver, events, RowMaker(X), saver, clock=clock, life=self.life)
#                 self.assertTrue(entered.is_set())
#                 self.assertEqual(database.saves, [])
#                 self.assertLessEqual(max(driver.waits), 1)
#                 self.assertGreaterEqual(self.life.heartbeat, 30)
#                 self.assertEqual(self.life.last_raised, clock.t)
#             finally:
#                 events.close()
#                 await saver.stop()
#         asyncio.run(work())
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_life.py::RoundsWithLife.test_a_database_save_that_never_answers_holds_up_no_round_or_raise

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:1
# import asyncio
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:1
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:2
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:2
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:7
# from unittest import mock
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:7
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:9
# from fake_driver import MovedClock, ScriptedDriver
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:9
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:10
# from fakes import FakeConnection, FakeDatabase
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:10
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:12
# from arbol_trunk_trivial.driver import Line
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:12
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:13
# from arbol_trunk_trivial.events import EventsFile
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:13
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:15
# from arbol_trunk_trivial.life import SignsOfLife, waiting_for
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:15
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:16
# from arbol_trunk_trivial.rows import Row, RowMaker
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:16
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:17
# from arbol_trunk_trivial.run import drive
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:17
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_life.py:18
# from arbol_trunk_trivial.saver import Saver
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_life.py:18
