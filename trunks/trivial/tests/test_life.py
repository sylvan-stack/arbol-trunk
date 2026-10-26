import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fake_driver import MovedClock

from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.life import SignsOfLife, waiting_for

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
    def test_only_the_work_raises_the_counter_and_publishes_its_awake_time(self) -> None:
        before = (self.folder.path / "record.json").read_bytes()
        self.clock.t += 59
        self.assertEqual(self.life.heartbeat, 0)
        self.assertEqual(self.life.last_raised, self.clock.start)
        self.assertEqual((self.folder.path / "record.json").read_bytes(), before)
        for n in range(1, 4):
            self.life.beat()
            record = json.loads((self.folder.path / "record.json").read_text())
            self.assertEqual(record, {**self.folder.record, "signsOfLife": {
                "heartbeat": n, "waitingFor": "database", "since": AT}})
            self.assertEqual(self.life.last_raised, self.clock.t)
            self.clock.t += 1

    def test_a_raise_replaces_the_record_whole_and_preserves_its_other_fields(self) -> None:
        with (self.folder.path / "record.json").open("rb") as reader:
            before = reader.read()
            self.life.beat()
            reader.seek(0)
            self.assertEqual(reader.read(), before)
        self.assertEqual(self.folder.record["exchange"], X)
        self.assertEqual(sorted(p.name for p in self.folder.path.iterdir()), ["control", "events.jsonl", "record.json"])

    def test_a_watch_can_exist_before_the_exchange_has_a_folder(self) -> None:
        life = SignsOfLife(clock=self.clock)
        life.bind(self.folder)
        life.beat()
        self.assertEqual(life.heartbeat, 1)
        self.assertEqual(self.folder.record["signsOfLife"]["heartbeat"], 1)


class Waiting(LifeHome):
    def test_the_first_true_wait_in_the_contracts_order_wins(self) -> None:
        cases = [({}, "database"), ({"small_call": True}, "small-call"), ({"driver": True}, "driver"),
                 ({"tool": True}, "tool"), ({"answer": True}, "answer"),
                 ({"driver": True, "small_call": True}, "driver"),
                 ({"tool": True, "driver": True, "small_call": True}, "tool"),
                 ({"answer": True, "tool": True, "driver": True, "small_call": True}, "answer")]
        for flags, expected in cases:
            with self.subTest(flags=flags):
                self.assertEqual(waiting_for(**flags), expected)

    def test_since_changes_only_when_the_wait_changes(self) -> None:
        with mock.patch("arbol_trunk_trivial.life.iso", return_value="2026-10-26T11:01:00.000Z"):
            self.life.beat("driver")
        with mock.patch("arbol_trunk_trivial.life.iso", return_value="2026-10-26T11:02:00.000Z"):
            self.life.beat("driver")
            self.assertEqual(self.folder.record["signsOfLife"]["since"], "2026-10-26T11:01:00.000Z")
            self.life.beat("tool")
        self.assertEqual(self.folder.record["signsOfLife"], {
            "heartbeat": 3, "waitingFor": "tool", "since": "2026-10-26T11:02:00.000Z"})

    def test_questions_and_calls_follow_their_events_until_they_close(self) -> None:
        events = [
            ({"type": "tool_started", "callId": "call"}, "tool"),
            ({"type": "ask_opened", "askId": "question"}, "answer"),
            ({"type": "text", "text": "still waiting"}, "answer"),
            ({"type": "ask_closed", "askId": "question"}, "tool"),
            ({"type": "tool_finished", "callId": "call"}, "driver"),
            ({"type": "tool_started", "callId": "cut-off"}, "tool"),
            ({"type": "finished"}, "driver")]
        for event, expected in events:
            self.life.observe({"runId": "run", **event})
            self.assertEqual(self.life.waiting(driver=True), expected)
        self.assertEqual(self.life.waiting(), "database")
