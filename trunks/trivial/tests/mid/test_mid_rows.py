"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_rows as _support
from test_rows import (
    ASK,
    Any,
    DEV,
    Jsonb,
    LINES,
    MAIN,
    MessageRow,
    Questions,
    RUN,
    RowMaker,
    Rows,
    RunRow,
    STARTED,
    ToolCallRow,
    UTC,
    X,
    asked,
    datetime,
    json,
    plain,
    unittest,
)


class Rows(_support.Rows):
# TEST-TIER-BEGIN trunks/trivial/tests/test_rows.py::Rows.test_the_rows_of_the_example_of_rct_1_at_their_positions
    def test_the_rows_of_the_example_of_rct_1_at_their_positions(self) -> None:
        _maker, rows = self.take(LINES)
        self.assertEqual(rows, [
            MessageRow(X, 3, "Let me read it."),
            ToolCallRow(X, 4, RUN, "call_1", None, "shell", {"command": "cat build.sh"}, True,
                        {"output": "#!/bin/sh\nset -e\n…", "exitCode": 0}),
            MessageRow(X, 6, "It compiles the three packages and copies them to dist/."),
            RunRow(X, RUN, "agent", "completed", {"model": "sonnet", "inputTokens": 5120, "outputTokens": 812}, None,
                   STARTED, datetime(2026, 10, 15, 9, 30, 9, 800000, tzinfo=UTC), line=7),
        ])
# TEST-TIER-END trunks/trivial/tests/test_rows.py::Rows.test_the_rows_of_the_example_of_rct_1_at_their_positions

# TEST-TIER-BEGIN trunks/trivial/tests/test_rows.py::Rows.test_a_sub_agents_text_is_no_row_and_its_calls_keep_their_parent
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
# TEST-TIER-END trunks/trivial/tests/test_rows.py::Rows.test_a_sub_agents_text_is_no_row_and_its_calls_keep_their_parent

# TEST-TIER-BEGIN trunks/trivial/tests/test_rows.py::Rows.test_a_run_without_usage_in_its_finished_takes_its_last_usage_event_else_nothing
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
# TEST-TIER-END trunks/trivial/tests/test_rows.py::Rows.test_a_run_without_usage_in_its_finished_takes_its_last_usage_event_else_nothing

# TEST-TIER-BEGIN trunks/trivial/tests/test_rows.py::Rows.test_at_the_end_open_calls_and_runs_without_finished_are_interrupted
    def test_at_the_end_open_calls_and_runs_without_finished_are_interrupted(self) -> None:
        maker, rows = self.take(LINES[:4])
        self.assertEqual(rows, [MessageRow(X, 3, "Let me read it.")])
        self.assertEqual(maker.at_end([RUN]), [
            ToolCallRow(X, 4, RUN, "call_1", None, "shell", {"command": "cat build.sh"}, False,
                        error="The Exchange ended before the tool call finished.", interrupted=True),
            RunRow(X, RUN, "agent", "interrupted", {}, None, STARTED,
                   datetime(2026, 10, 15, 9, 30, 3, 400000, tzinfo=UTC), line=4),
        ])
        self.assertEqual(maker.at_end([RUN]), [])
# TEST-TIER-END trunks/trivial/tests/test_rows.py::Rows.test_at_the_end_open_calls_and_runs_without_finished_are_interrupted

# TEST-TIER-BEGIN trunks/trivial/tests/test_rows.py::Rows.test_the_statements_insert_and_do_nothing_when_the_row_is_there
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
# TEST-TIER-END trunks/trivial/tests/test_rows.py::Rows.test_the_statements_insert_and_do_nothing_when_the_row_is_there



class Questions(_support.Questions):
# TEST-TIER-BEGIN trunks/trivial/tests/test_rows.py::Questions.test_the_row_holds_the_question_and_its_answer
    def test_the_row_holds_the_question_and_its_answer(self) -> None:
        _maker, rows = self.rows([*self.opened(), ("answer", {"type": "answer", "askId": "ask_3", "answer": MAIN}),
                                  asked(4, "ask_closed", askId="ask_3", reason="answered"), self.finish(5)])
        [row] = rows
        self.assertEqual((row.position, row.name, row.ask, row.answer), (1, "ask_user", ASK, MAIN))
# TEST-TIER-END trunks/trivial/tests/test_rows.py::Questions.test_the_row_holds_the_question_and_its_answer

# TEST-TIER-BEGIN trunks/trivial/tests/test_rows.py::Questions.test_the_answer_is_the_last_one_that_no_control_refused_follows
    def test_the_answer_is_the_last_one_that_no_control_refused_follows(self) -> None:
        refused = asked(4, "control_refused", askId="ask_3", error={"code": "invalid_input", "message": "No."})
        _maker, rows = self.rows([*self.opened(), ("answer", {"type": "answer", "askId": "ask_3", "answer": MAIN}),
                                  refused, ("answer", {"type": "answer", "askId": "ask_3", "answer": DEV}),
                                  self.finish(6)])
        self.assertEqual(rows[0].answer, DEV)
        _maker, rows = self.rows([*self.opened(), ("answer", {"type": "answer", "askId": "ask_3", "answer": MAIN}),
                                  ("answer", {"type": "answer", "askId": "ask_3", "answer": DEV}), refused,
                                  self.finish(6)])
        self.assertIsNone(rows[0].answer)
# TEST-TIER-END trunks/trivial/tests/test_rows.py::Questions.test_the_answer_is_the_last_one_that_no_control_refused_follows

# TEST-TIER-BEGIN trunks/trivial/tests/test_rows.py::Questions.test_another_call_and_an_answer_to_another_question_leave_ask_and_answer_null
    def test_another_call_and_an_answer_to_another_question_leave_ask_and_answer_null(self) -> None:
        _maker, rows = self.rows([*LINES[3:5], ("answer", {"type": "answer", "askId": "ask_9", "answer": MAIN})])
        self.assertEqual((rows[0].ask, rows[0].answer), (None, None))
# TEST-TIER-END trunks/trivial/tests/test_rows.py::Questions.test_another_call_and_an_answer_to_another_question_leave_ask_and_answer_null

# TEST-TIER-BEGIN trunks/trivial/tests/test_rows.py::Questions.test_a_question_the_end_cut_off_keeps_its_ask_and_has_no_answer
    def test_a_question_the_end_cut_off_keeps_its_ask_and_has_no_answer(self) -> None:
        maker, _rows = self.rows(self.opened())
        [row] = [row for row in maker.at_end() if isinstance(row, ToolCallRow)]
        self.assertEqual((row.interrupted, row.ask, row.answer), (True, ASK, None))
        self.assertEqual(plain(row.statement()[1])[12:], [ASK, None])
# TEST-TIER-END trunks/trivial/tests/test_rows.py::Questions.test_a_question_the_end_cut_off_keeps_its_ask_and_has_no_answer
