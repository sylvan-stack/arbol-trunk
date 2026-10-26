import asyncio
import json
import os
import tempfile
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

from fakes import Exchange, FakeDatabase

from arbol_trunk_trivial.cli import start
from arbol_trunk_trivial.command import parse
from arbol_trunk_trivial.errors import Refusal
from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.output import Output
from arbol_trunk_trivial.process import started_at
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.rows import MessageRow, RunRow, ToolCallRow
from arbol_trunk_trivial.settle import Settlement, open_settlement, replay

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
AT = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)


class SettlementTest(unittest.TestCase):
    def setUp(self) -> None:
        name = tempfile.TemporaryDirectory()
        self.addCleanup(name.cleanup)
        self.home = Path(name.name)
        self.root = roots_folder(self.home) / "rct"
        self.exchanges = self.root / "exchanges"
        self.exchanges.mkdir(parents=True)
        (self.root / "root.json").write_text(json.dumps({"database": "arbol_rct", "rootContract": 1}))
        self.record = {"exchange": X, "process": {"pid": os.getpid(), "startedAt": "2000-01-01T00:00:00Z"},
                       "acceptedAt": AT.isoformat()}
        self.folder = ExchangeFolder.make(self.exchanges, X, self.record)
        self.database = FakeDatabase()
        self.database.exchanges[X] = Exchange(X, "chat", 1, "open", "trivial", "0", {}, None, "/w", AT)

    def open(self) -> Settlement | None:
        return asyncio.run(open_settlement(self.home, "rct", X, connect=self.database.connect()))


class OpeningSettlement(SettlementTest):
    def test_the_command_takes_exactly_one_exchange_uuid(self) -> None:
        command = parse(["--root", "rct", "settle", X])
        self.assertEqual((command.root, command.operation, command.options), ("rct", "settle", {"--exchange": X}))
        for args in (["settle"], ["settle", "../x"], ["settle", X.upper()], ["settle", X, "more"]):
            with self.subTest(args=args), self.assertRaises(Refusal):
                parse(["--root", "rct", *args])

    def test_no_folder_needs_no_database_or_driver_settings(self) -> None:
        self.folder.remove()
        self.assertIsNone(self.open())
        self.assertEqual(self.database.connections, 0)

    def test_a_living_process_is_refused_before_any_database_access(self) -> None:
        self.folder.record["process"]["startedAt"] = started_at()
        (self.folder.path / "record.json").write_text(json.dumps(self.folder.record))
        with self.assertRaises(Refusal) as caught:
            self.open()
        self.assertEqual(caught.exception.code, "alive")
        self.assertEqual(self.database.connections, 0)
        self.assertTrue(self.folder.path.exists())

    def test_a_reused_pid_does_not_count_as_a_living_owner(self) -> None:
        pending = self.open()
        assert pending is not None
        self.assertEqual(pending.stored.state, "open")
        asyncio.run(pending.connection.close())

    def test_an_unavailable_database_keeps_the_folder(self) -> None:
        self.database.fail_connect = 1
        with self.assertRaises(Refusal) as caught:
            self.open()
        self.assertEqual(caught.exception.code, "database_unavailable")
        self.assertTrue(self.folder.path.exists())

    def test_a_database_that_never_answers_is_bounded_and_its_connection_closed(self) -> None:
        self.database.delay = 0.1
        with mock.patch("arbol_trunk_trivial.settle.DATABASE_SECONDS", 0.15), self.assertRaises(Refusal) as caught:
            self.open()
        self.assertEqual(caught.exception.code, "database_unavailable")
        self.assertEqual(self.database.closed, 1)


    def test_a_folder_whose_exchange_was_never_accepted_is_removed(self) -> None:
        self.database.exchanges.clear()
        self.assertIsNone(self.open())
        self.assertFalse(self.folder.path.exists())
        self.assertEqual(self.database.closed, 1)


class ReplayingSettlement(SettlementTest):
    def write(self, *lines: object, tail: bytes = b"") -> None:
        data = b"".join(json.dumps(line).encode() + b"\n" for line in lines)
        (self.folder.path / "events.jsonl").write_bytes(data + tail)

    def test_replay_recovers_text_questions_open_calls_and_unfinished_run_usage(self) -> None:
        ask = {"callId": "call_1", "questions": [{"id": "q", "question": "Which?"}]}
        answer = {"type": "answers", "answers": {"q": ["main"]}}
        self.write(
            {"n": 1, "event": {"type": "started", "runId": "run", "at": AT.isoformat()}},
            {"n": 2, "event": {"type": "text", "runId": "run", "text": "hello"}},
            {"n": 3, "event": {"type": "tool_started", "runId": "run", "callId": "call_1", "name": "ask",
                                "input": {}}},
            {"n": 4, "event": {"type": "ask_opened", "runId": "run", "askId": "ask_1", "ask": ask}},
            {"n": 5, "answer": {"type": "answer", "askId": "ask_1", "answer": answer}},
            {"n": 6, "event": {"type": "usage", "runId": "run", "at": "2026-10-15T09:31:00Z",
                                "usage": {"inputTokens": 123}}},
        )
        found = replay(self.folder.path / "events.jsonl", X, AT)
        self.assertEqual(found.rows[0], MessageRow(X, 2, "hello"))
        call, run = found.rows[1:]
        assert isinstance(call, ToolCallRow) and isinstance(run, RunRow)
        self.assertEqual((call.position, call.interrupted, call.ok, call.ask, call.answer),
                         (3, True, False, ask, answer))
        self.assertEqual((run.outcome, run.usage, run.ended_at),
                         ("interrupted", {"inputTokens": 123}, datetime(2026, 10, 15, 9, 31, tzinfo=UTC)))
        self.assertEqual(found.last_at, run.ended_at)

    def test_whole_lines_only_and_unknown_lines_are_ignored(self) -> None:
        self.write({"n": 1, "event": {"type": "text", "runId": "run", "text": "kept"}},
                   {"n": 2, "futureField": {"something": True}}, ["unknown"],
                   tail=b'{"n":3,"event":{"type":"text","runId":"run","text":"unfinished"}}')
        found = replay(self.folder.path / "events.jsonl", X, AT)
        self.assertEqual([r.text for r in found.rows if isinstance(r, MessageRow)], ["kept"])
        self.assertEqual(found.last_at, AT)
        self.assertEqual([r.ended_at for r in found.rows if isinstance(r, RunRow)], [AT])

    def test_finished_agent_and_small_calls_keep_their_own_outcome_and_usage(self) -> None:
        finished = {"type": "finished", "runId": "agent", "outcome": "completed", "at": AT.isoformat(),
                    "usage": {"inputTokens": 12}}
        small = {**finished, "runId": "small", "outcome": "failed", "usage": {"inputTokens": 3},
                 "error": {"code": "rate_limited", "message": "later"}}
        end = {"state": "completed", "at": "2026-10-15T09:32:00Z"}
        self.write({"n": 1, "event": finished}, {"n": 2, "smallRun": small}, {"n": 3, "end": end})
        found = replay(self.folder.path / "events.jsonl", X, AT)
        runs = [r for r in found.rows if isinstance(r, RunRow)]
        self.assertEqual([(r.run_id, r.kind, r.outcome, r.usage) for r in runs],
                         [("agent", "agent", "completed", {"inputTokens": 12}),
                          ("small", "small", "failed", {"inputTokens": 3})])
        self.assertEqual(runs[1].error, small["error"])
        self.assertEqual(found.end, end)


class SavingSettlement(SettlementTest):
    def settle(self) -> tuple[int, dict[str, object]]:
        lines: list[str] = []
        status = asyncio.run(start(["--root", "rct", "settle", X], home=self.home, started=time.monotonic(),
                                   output=Output(lines.append), settle_connect=self.database.connect()))
        self.assertEqual(len(lines), 1)
        return status, json.loads(lines[0])

    def test_the_command_saves_missing_rows_and_the_interrupted_end_then_removes_the_folder(self) -> None:
        lines = [
            {"n": 1, "event": {"runId": "run", "type": "started", "at": AT.isoformat()}},
            {"n": 2, "event": {"runId": "run", "type": "text", "text": "first"}},
            {"n": 3, "event": {"runId": "run", "type": "text", "text": "second"}},
            {"n": 4, "event": {"runId": "run", "type": "tool_started", "callId": "call", "name": "shell",
                                "input": {"command": "make"}, "at": "2026-10-15T09:31:00Z"}},
        ]
        (self.folder.path / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))
        self.database.messages[(X, 2)] = ("assistant", "already saved")
        self.assertEqual(self.settle(), (0, {"exchange": X, "settled": "interrupted"}))
        self.assertEqual(self.database.messages[(X, 2)], ("assistant", "already saved"))
        self.assertEqual(self.database.messages[(X, 3)], ("assistant", "second"))
        self.assertTrue(self.database.tool_calls[(X, 4)]["interrupted"])
        self.assertEqual(self.database.runs[(X, "run")]["outcome"], "interrupted")
        self.assertEqual(self.database.exchanges[X].ended_at, datetime(2026, 10, 15, 9, 31, tzinfo=UTC))
        self.assertFalse(self.folder.path.exists())
        self.assertEqual(self.database.closed, 1)
        self.assertEqual(self.settle(), (0, {"exchange": X, "settled": "none"}))

    def test_a_recorded_end_stands_and_an_empty_file_falls_back_to_accepted_at(self) -> None:
        self.folder.update(end={"state": "failed", "at": AT.isoformat(),
                                "error": {"code": "driver_failed", "message": "The Driver failed."}})
        self.assertEqual(self.settle()[1]["settled"], "failed")
        self.assertEqual(self.database.exchanges[X].error["code"], "driver_failed")
        self.assertEqual(self.database.exchanges[X].ended_at, AT)

    def test_the_end_line_is_used_when_the_record_has_no_end(self) -> None:
        (self.folder.path / "events.jsonl").write_text(json.dumps(
            {"n": 1, "end": {"state": "cancelled", "at": AT.isoformat()}}) + "\n")
        self.assertEqual(self.settle()[1]["settled"], "cancelled")

    def test_without_an_end_or_a_timestamp_the_database_acceptance_time_is_used(self) -> None:
        self.assertEqual(self.settle()[1]["settled"], "interrupted")
        self.assertEqual(self.database.exchanges[X].ended_at, AT)

    def test_an_exchange_that_already_ended_keeps_its_state_and_end_time(self) -> None:
        existing = self.database.exchanges[X]
        existing.state, existing.ended_at = "completed", AT
        self.assertEqual(self.settle()[1]["settled"], "completed")
        self.assertEqual((existing.state, existing.ended_at), ("completed", AT))

    def test_a_failed_save_keeps_the_folder_for_another_settle(self) -> None:
        self.database.fail_end = 1
        status, answer = self.settle()
        self.assertEqual(status, 1)
        self.assertEqual(answer["error"]["code"], "database_unavailable")  # type: ignore[index]
        self.assertTrue(self.folder.path.exists())

        self.assertEqual(self.database.closed, 1)
        self.assertEqual(self.database.exchanges[X].state, "open")
        self.assertTrue(self.folder.path.exists())

    def test_a_replaced_exchange_recovers_only_runs_and_keeps_its_ended_state(self) -> None:
        stored = self.database.exchanges[X]
        stored.state, stored.ended_at, stored.replaced_by = "completed", AT, "replacement"
        lines = [
            {"n": 1, "event": {"type": "started", "runId": "run", "at": AT.isoformat()}},
            {"n": 2, "event": {"type": "text", "runId": "run", "text": "discarded"}},
            {"n": 3, "event": {"type": "tool_started", "runId": "run", "callId": "call", "name": "shell",
                                "input": {}, "at": AT.isoformat()}},
            {"n": 4, "event": {"type": "usage", "runId": "run", "usage": {"inputTokens": 41},
                                "at": AT.isoformat()}},
        ]
        (self.folder.path / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))
        self.assertEqual(self.settle(), (0, {"exchange": X, "settled": "completed"}))
        self.assertEqual(self.database.messages, {})
        self.assertEqual(self.database.tool_calls, {})
        self.assertEqual(self.database.runs[(X, "run")]["usage"], {"inputTokens": 41})
        self.assertEqual((stored.state, stored.ended_at, stored.replaced_by), ("completed", AT, "replacement"))
