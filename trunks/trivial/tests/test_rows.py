import json
import unittest
from datetime import UTC, datetime
from typing import Any

from psycopg.types.json import Jsonb

from arbol_trunk_trivial.rows import MessageRow, RowMaker, RunRow, ToolCallRow

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
RUN = f"{X}.1"
STARTED = {"runId": RUN, "seq": 1, "at": "2026-10-15T09:30:01.204Z", "type": "started", "continuity": "fresh",
           "subscriptionId": "anthropic", "model": "sonnet", "effort": "high", "toolVersion": "2.1.294",
           "driverBuild": "b"}
LINES: list[dict[str, Any]] = [  # the example of RCT-1
    STARTED,
    {"runId": RUN, "seq": 2, "at": "2026-10-15T09:30:03.020Z", "type": "text_delta", "text": "Let me "},
    {"runId": RUN, "seq": 3, "at": "2026-10-15T09:30:03.310Z", "type": "text", "text": "Let me read it."},
    {"runId": RUN, "seq": 4, "at": "2026-10-15T09:30:03.400Z", "type": "tool_started", "callId": "call_1",
     "name": "shell", "input": {"command": "cat build.sh"}},
    {"runId": RUN, "seq": 5, "at": "2026-10-15T09:30:03.900Z", "type": "tool_finished", "callId": "call_1",
     "ok": True, "result": {"output": "#!/bin/sh\nset -e\n…", "exitCode": 0}},
    {"runId": RUN, "seq": 6, "at": "2026-10-15T09:30:09.700Z", "type": "text",
     "text": "It compiles the three packages and copies them to dist/."},
    {"runId": RUN, "seq": 7, "at": "2026-10-15T09:30:09.800Z", "type": "finished", "outcome": "completed",
     "usage": {"model": "sonnet", "inputTokens": 5120, "outputTokens": 812}, "producedOutput": True,
     "unfinishedCalls": []},
]


def plain(value: Any) -> Any:
    return json.loads(json.dumps(value, default=lambda o: o.obj if isinstance(o, Jsonb) else str(o)))


class Rows(unittest.TestCase):
    def take(self, lines: list[dict[str, Any]]) -> tuple[RowMaker, list[Any]]:
        maker = RowMaker(X)
        rows: list[Any] = []
        for n, event in enumerate(lines, 1):
            rows += maker.take(n, event)
        return maker, rows

    def test_the_rows_of_the_example_of_rct_1_at_their_positions(self) -> None:
        _maker, rows = self.take(LINES)
        self.assertEqual(rows, [
            MessageRow(X, 3, "Let me read it."),
            ToolCallRow(X, 4, RUN, "call_1", None, "shell", {"command": "cat build.sh"}, True,
                        {"output": "#!/bin/sh\nset -e\n…", "exitCode": 0}),
            MessageRow(X, 6, "It compiles the three packages and copies them to dist/."),
            RunRow(X, RUN, "agent", "completed", {"model": "sonnet", "inputTokens": 5120, "outputTokens": 812}, None,
                   STARTED, datetime(2026, 10, 15, 9, 30, 9, 800000, tzinfo=UTC)),
        ])

    def test_a_sub_agents_text_is_no_row_and_its_calls_keep_their_parent(self) -> None:
        _maker, rows = self.take([
            STARTED,
            {"runId": RUN, "seq": 2, "type": "text", "text": "sub", "parentCallId": "call_9"},
            {"runId": RUN, "seq": 3, "type": "tool_started", "callId": "c", "name": "Read", "input": {},
             "parentCallId": "call_9"},
            {"runId": RUN, "seq": 4, "type": "tool_finished", "callId": "c", "ok": False, "error": "no",
             "truncated": True, "interrupted": True},
        ])
        self.assertEqual(rows, [ToolCallRow(X, 3, RUN, "c", "call_9", "Read", {}, False, None, "no", True, True)])

    def test_a_run_without_usage_in_its_finished_takes_its_last_usage_event_else_nothing(self) -> None:
        _maker, rows = self.take([
            STARTED, {"runId": RUN, "seq": 2, "type": "usage", "usage": {"inputTokens": 5}},
            {"runId": RUN, "seq": 3, "at": "2026-10-15T09:31:00.000Z", "type": "finished", "outcome": "failed",
             "error": {"code": "rate_limited", "message": "…", "retryable": True, "retryAfterSeconds": 1800},
             "producedOutput": False, "unfinishedCalls": []},
        ])
        self.assertEqual(rows[0].usage, {"inputTokens": 5})
        self.assertEqual(rows[0].error["retryAfterSeconds"], 1800)
        _maker, rows = self.take([{"runId": RUN, "seq": 1, "type": "finished", "outcome": "cancelled",
                                   "producedOutput": False, "unfinishedCalls": []}])
        self.assertEqual((rows[0].usage, rows[0].error, rows[0].started), ({}, None, None))

    def test_at_the_end_open_calls_and_runs_without_finished_are_interrupted(self) -> None:
        maker, rows = self.take(LINES[:4])
        self.assertEqual(rows, [MessageRow(X, 3, "Let me read it.")])
        self.assertEqual(maker.at_end([RUN]), [
            ToolCallRow(X, 4, RUN, "call_1", None, "shell", {"command": "cat build.sh"}, False,
                        error="The Exchange ended before the tool call finished.", interrupted=True),
            RunRow(X, RUN, "agent", "interrupted", {}, None, STARTED,
                   datetime(2026, 10, 15, 9, 30, 3, 400000, tzinfo=UTC)),
        ])
        self.assertEqual(maker.at_end([RUN]), [])

    def test_the_statements_insert_and_do_nothing_when_the_row_is_there(self) -> None:
        _maker, rows = self.take(LINES)
        for row in rows:
            sql, _params = row.statement()
            self.assertTrue(sql.startswith("INSERT INTO "))
            self.assertTrue(sql.endswith(" ON CONFLICT DO NOTHING"))
        sql, params = rows[1].statement()
        self.assertIn("INSERT INTO tool_calls (exchange_id, position, run_id, call_id", sql)
        self.assertEqual(plain(params), [X, 4, RUN, "call_1", None, "shell", {"command": "cat build.sh"}, True,
                                         {"output": "#!/bin/sh\nset -e\n…", "exitCode": 0}, None, False, False, None,
                                         None])
        _sql, params = rows[3].statement()
        self.assertEqual(plain(params)[:6], [X, RUN, "agent", "completed",
                                             {"model": "sonnet", "inputTokens": 5120, "outputTokens": 812}, None])
        self.assertEqual(rows[0].statement()[1], (X, 3, "Let me read it."))


if __name__ == "__main__":
    unittest.main()
