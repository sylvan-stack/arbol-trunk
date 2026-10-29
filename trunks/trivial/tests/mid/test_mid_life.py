"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_life as _support
from test_life import (
    AT,
    EventsFile,
    ExchangeFolder,
    FakeConnection,
    FakeDatabase,
    Heartbeat,
    LifeHome,
    Line,
    MovedClock,
    Path,
    RoundsWithLife,
    Row,
    RowMaker,
    Saver,
    ScriptedDriver,
    SignsOfLife,
    Waiting,
    X,
    asyncio,
    drive,
    json,
    mock,
    os,
    tempfile,
    unittest,
    waiting_for,
)


class Heartbeat(_support.Heartbeat):
# TEST-TIER-BEGIN trunks/trivial/tests/test_life.py::Heartbeat.test_only_the_work_raises_the_counter_and_publishes_its_awake_time
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
# TEST-TIER-END trunks/trivial/tests/test_life.py::Heartbeat.test_only_the_work_raises_the_counter_and_publishes_its_awake_time

# TEST-TIER-BEGIN trunks/trivial/tests/test_life.py::Heartbeat.test_a_raise_replaces_the_record_whole_and_preserves_its_other_fields
    def test_a_raise_replaces_the_record_whole_and_preserves_its_other_fields(self) -> None:
        with (self.folder.path / "record.json").open("rb") as reader:
            before = reader.read()
            self.life.beat()
            reader.seek(0)
            self.assertEqual(reader.read(), before)
        self.assertEqual(self.folder.record["exchange"], X)
        self.assertEqual(sorted(p.name for p in self.folder.path.iterdir()), ["control", "events.jsonl", "record.json"])
# TEST-TIER-END trunks/trivial/tests/test_life.py::Heartbeat.test_a_raise_replaces_the_record_whole_and_preserves_its_other_fields

# TEST-TIER-BEGIN trunks/trivial/tests/test_life.py::Heartbeat.test_a_watch_can_exist_before_the_exchange_has_a_folder
    def test_a_watch_can_exist_before_the_exchange_has_a_folder(self) -> None:
        life = SignsOfLife(clock=self.clock)
        life.bind(self.folder)
        life.beat()
        self.assertEqual(life.heartbeat, 1)
        self.assertEqual(self.folder.record["signsOfLife"]["heartbeat"], 1)
# TEST-TIER-END trunks/trivial/tests/test_life.py::Heartbeat.test_a_watch_can_exist_before_the_exchange_has_a_folder



class Waiting(_support.Waiting):
# TEST-TIER-BEGIN trunks/trivial/tests/test_life.py::Waiting.test_the_first_true_wait_in_the_contracts_order_wins
    def test_the_first_true_wait_in_the_contracts_order_wins(self) -> None:
        cases = [({}, "database"), ({"small_call": True}, "small-call"), ({"driver": True}, "driver"),
                 ({"tool": True}, "tool"), ({"answer": True}, "answer"),
                 ({"driver": True, "small_call": True}, "driver"),
                 ({"tool": True, "driver": True, "small_call": True}, "tool"),
                 ({"answer": True, "tool": True, "driver": True, "small_call": True}, "answer")]
        for flags, expected in cases:
            with self.subTest(flags=flags):
                self.assertEqual(waiting_for(**flags), expected)
# TEST-TIER-END trunks/trivial/tests/test_life.py::Waiting.test_the_first_true_wait_in_the_contracts_order_wins

# TEST-TIER-BEGIN trunks/trivial/tests/test_life.py::Waiting.test_since_changes_only_when_the_wait_changes
    def test_since_changes_only_when_the_wait_changes(self) -> None:
        with mock.patch("arbol_trunk_trivial.life.iso", return_value="2026-10-26T11:01:00.000Z"):
            self.life.beat("driver")
        with mock.patch("arbol_trunk_trivial.life.iso", return_value="2026-10-26T11:02:00.000Z"):
            self.life.beat("driver")
            self.assertEqual(self.folder.record["signsOfLife"]["since"], "2026-10-26T11:01:00.000Z")
            self.life.beat("tool")
        self.assertEqual(self.folder.record["signsOfLife"], {
            "heartbeat": 3, "waitingFor": "tool", "since": "2026-10-26T11:02:00.000Z"})
# TEST-TIER-END trunks/trivial/tests/test_life.py::Waiting.test_since_changes_only_when_the_wait_changes

# TEST-TIER-BEGIN trunks/trivial/tests/test_life.py::Waiting.test_questions_and_calls_follow_their_events_until_they_close
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
# TEST-TIER-END trunks/trivial/tests/test_life.py::Waiting.test_questions_and_calls_follow_their_events_until_they_close



class RoundsWithLife(_support.RoundsWithLife):
# TEST-TIER-BEGIN trunks/trivial/tests/test_life.py::RoundsWithLife.test_a_database_save_that_never_answers_holds_up_no_round_or_raise
    def test_a_database_save_that_never_answers_holds_up_no_round_or_raise(self) -> None:
        clock = self.clock

        class YieldingDriver(ScriptedDriver):
            async def read(self, seconds: float) -> list[Line]:
                await asyncio.sleep(0)
                return await super().read(seconds)

        async def work() -> None:
            entered = asyncio.Event()

            async def slow(connection: FakeConnection, row: Row) -> None:
                entered.set()
                await asyncio.Future[None]()

            driver = YieldingDriver(clock)
            driver.at(0, "event", {"runId": "run", "type": "text", "text": "save this"})
            driver.at(30, "event", {"runId": "run", "type": "finished", "outcome": "completed"})
            driver.at(30, "exit", 0)
            database = FakeDatabase()
            saver = Saver(database.connect())
            events = EventsFile(self.folder.path / "events.jsonl")
            saver.start()
            try:
                with mock.patch.object(FakeConnection, "save", slow):
                    await drive(driver, events, RowMaker(X), saver, clock=clock, life=self.life)
                self.assertTrue(entered.is_set())
                self.assertEqual(database.saves, [])
                self.assertLessEqual(max(driver.waits), 1)
                self.assertGreaterEqual(self.life.heartbeat, 30)
                self.assertEqual(self.life.last_raised, clock.t)
            finally:
                events.close()
                await saver.stop()
        asyncio.run(work())
# TEST-TIER-END trunks/trivial/tests/test_life.py::RoundsWithLife.test_a_database_save_that_never_answers_holds_up_no_round_or_raise
