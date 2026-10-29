
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::OpeningSettlement.test_the_command_takes_exactly_one_exchange_uuid
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: The command takes exactly one exchange uuid.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_command_takes_exactly_one_exchange_uuid(self) -> None:
#         command = parse(["--root", "rct", "settle", X])
#         self.assertEqual((command.root, command.operation, command.options), ("rct", "settle", {"--exchange": X}))
#         for args in (["settle"], ["settle", "../x"], ["settle", X.upper()], ["settle", X, "more"]):
#             with self.subTest(args=args), self.assertRaises(Refusal):
#                 parse(["--root", "rct", *args])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::OpeningSettlement.test_no_folder_needs_no_database_or_driver_settings
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: No folder needs no database or driver settings.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_no_folder_needs_no_database_or_driver_settings(self) -> None:
#         self.folder.remove()
#         self.assertIsNone(self.open())
#         self.assertEqual(self.database.connections, 0)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::OpeningSettlement.test_a_living_process_is_refused_before_any_database_access
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: A living process is refused before any database access.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_living_process_is_refused_before_any_database_access(self) -> None:
#         self.folder.record["process"]["startedAt"] = started_at()
#         (self.folder.path / "record.json").write_text(json.dumps(self.folder.record))
#         with self.assertRaises(Refusal) as caught:
#             self.open()
#         self.assertEqual(caught.exception.code, "alive")
#         self.assertEqual(self.database.connections, 0)
#         self.assertTrue(self.folder.path.exists())
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::OpeningSettlement.test_a_reused_pid_does_not_count_as_a_living_owner
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: A reused pid does not count as a living owner.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_reused_pid_does_not_count_as_a_living_owner(self) -> None:
#         pending = self.open()
#         assert pending is not None
#         self.assertEqual(pending.stored.state, "open")
#         asyncio.run(pending.connection.close())
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::OpeningSettlement.test_an_unavailable_database_keeps_the_folder
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: An unavailable database keeps the folder.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_an_unavailable_database_keeps_the_folder(self) -> None:
#         self.database.fail_connect = 1
#         with self.assertRaises(Refusal) as caught:
#             self.open()
#         self.assertEqual(caught.exception.code, "database_unavailable")
#         self.assertTrue(self.folder.path.exists())
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::OpeningSettlement.test_a_database_that_never_answers_is_bounded_and_its_connection_closed
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: A database that never answers is bounded and its connection closed.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_database_that_never_answers_is_bounded_and_its_connection_closed(self) -> None:
#         self.database.delay = 0.1
#         with mock.patch("arbol_trunk_trivial.settle.DATABASE_SECONDS", 0.15), self.assertRaises(Refusal) as caught:
#             self.open()
#         self.assertEqual(caught.exception.code, "database_unavailable")
#         self.assertEqual(self.database.closed, 1)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::OpeningSettlement.test_a_folder_whose_exchange_was_never_accepted_is_removed
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: A folder whose exchange was never accepted is removed.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_folder_whose_exchange_was_never_accepted_is_removed(self) -> None:
#         self.database.exchanges.clear()
#         self.assertIsNone(self.open())
#         self.assertFalse(self.folder.path.exists())
#         self.assertEqual(self.database.closed, 1)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::ReplayingSettlement.test_replay_recovers_text_questions_open_calls_and_unfinished_run_usage
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: Replay recovers text questions open calls and unfinished run usage.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_replay_recovers_text_questions_open_calls_and_unfinished_run_usage(self) -> None:
#         ask = {"callId": "call_1", "questions": [{"id": "q", "question": "Which?"}]}
#         answer = {"type": "answers", "answers": {"q": ["main"]}}
#         self.write(
#             {"n": 1, "event": {"type": "started", "runId": "run", "at": AT.isoformat()}},
#             {"n": 2, "event": {"type": "text", "runId": "run", "text": "hello"}},
#             {"n": 3, "event": {"type": "tool_started", "runId": "run", "callId": "call_1", "name": "ask",
#                                 "input": {}}},
#             {"n": 4, "event": {"type": "ask_opened", "runId": "run", "askId": "ask_1", "ask": ask}},
#             {"n": 5, "answer": {"type": "answer", "askId": "ask_1", "answer": answer}},
#             {"n": 6, "event": {"type": "usage", "runId": "run", "at": "2026-10-15T09:31:00Z",
#                                 "usage": {"inputTokens": 123}}},
#         )
#         found = replay(self.folder.path / "events.jsonl", X, AT)
#         self.assertEqual(found.rows[0], MessageRow(X, 2, "hello"))
#         call, run = found.rows[1:]
#         assert isinstance(call, ToolCallRow) and isinstance(run, RunRow)
#         self.assertEqual((call.position, call.interrupted, call.ok, call.ask, call.answer),
#                          (3, True, False, ask, answer))
#         self.assertEqual((run.outcome, run.usage, run.ended_at),
#                          ("interrupted", {"inputTokens": 123}, datetime(2026, 10, 15, 9, 31, tzinfo=UTC)))
#         self.assertEqual(found.last_at, run.ended_at)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::ReplayingSettlement.test_whole_lines_only_and_unknown_lines_are_ignored
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: Whole lines only and unknown lines are ignored.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_whole_lines_only_and_unknown_lines_are_ignored(self) -> None:
#         self.write({"n": 1, "event": {"type": "text", "runId": "run", "text": "kept"}},
#                    {"n": 2, "futureField": {"something": True}}, ["unknown"],
#                    tail=b'{"n":3,"event":{"type":"text","runId":"run","text":"unfinished"}}')
#         found = replay(self.folder.path / "events.jsonl", X, AT)
#         self.assertEqual([r.text for r in found.rows if isinstance(r, MessageRow)], ["kept"])
#         self.assertEqual(found.last_at, AT)
#         self.assertEqual([r.ended_at for r in found.rows if isinstance(r, RunRow)], [AT])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::ReplayingSettlement.test_finished_agent_and_small_calls_keep_their_own_outcome_and_usage
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: Finished agent and small calls keep their own outcome and usage.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_finished_agent_and_small_calls_keep_their_own_outcome_and_usage(self) -> None:
#         finished = {"type": "finished", "runId": "agent", "outcome": "completed", "at": AT.isoformat(),
#                     "usage": {"inputTokens": 12}}
#         small = {**finished, "runId": "small", "outcome": "failed", "usage": {"inputTokens": 3},
#                  "error": {"code": "rate_limited", "message": "later"}}
#         end = {"state": "completed", "at": "2026-10-15T09:32:00Z"}
#         self.write({"n": 1, "event": finished}, {"n": 2, "smallRun": small}, {"n": 3, "end": end})
#         found = replay(self.folder.path / "events.jsonl", X, AT)
#         runs = [r for r in found.rows if isinstance(r, RunRow)]
#         self.assertEqual([(r.run_id, r.kind, r.outcome, r.usage) for r in runs],
#                          [("agent", "agent", "completed", {"inputTokens": 12}),
#                           ("small", "small", "failed", {"inputTokens": 3})])
#         self.assertEqual(runs[1].error, small["error"])
#         self.assertEqual(found.end, end)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::SavingSettlement.test_the_command_saves_missing_rows_and_the_interrupted_end_then_removes_the_folder
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: The command saves missing rows and the interrupted end then removes the folder.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_command_saves_missing_rows_and_the_interrupted_end_then_removes_the_folder(self) -> None:
#         lines = [
#             {"n": 1, "event": {"runId": "run", "type": "started", "at": AT.isoformat()}},
#             {"n": 2, "event": {"runId": "run", "type": "text", "text": "first"}},
#             {"n": 3, "event": {"runId": "run", "type": "text", "text": "second"}},
#             {"n": 4, "event": {"runId": "run", "type": "tool_started", "callId": "call", "name": "shell",
#                                 "input": {"command": "make"}, "at": "2026-10-15T09:31:00Z"}},
#         ]
#         (self.folder.path / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))
#         self.database.messages[(X, 2)] = ("assistant", "already saved")
#         self.assertEqual(self.settle(), (0, {"exchange": X, "settled": "interrupted"}))
#         self.assertEqual(self.database.messages[(X, 2)], ("assistant", "already saved"))
#         self.assertEqual(self.database.messages[(X, 3)], ("assistant", "second"))
#         self.assertTrue(self.database.tool_calls[(X, 4)]["interrupted"])
#         self.assertEqual(self.database.runs[(X, "run")]["outcome"], "interrupted")
#         self.assertEqual(self.database.exchanges[X].ended_at, datetime(2026, 10, 15, 9, 31, tzinfo=UTC))
#         self.assertFalse(self.folder.path.exists())
#         self.assertEqual(self.database.closed, 1)
#         self.assertEqual(self.settle(), (0, {"exchange": X, "settled": "none"}))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::SavingSettlement.test_a_recorded_end_stands_and_an_empty_file_falls_back_to_accepted_at
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: A recorded end stands and an empty file falls back to accepted at.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_recorded_end_stands_and_an_empty_file_falls_back_to_accepted_at(self) -> None:
#         self.folder.update(end={"state": "failed", "at": AT.isoformat(),
#                                 "error": {"code": "driver_failed", "message": "The Driver failed."}})
#         self.assertEqual(self.settle()[1]["settled"], "failed")
#         self.assertEqual(self.database.exchanges[X].error["code"], "driver_failed")
#         self.assertEqual(self.database.exchanges[X].ended_at, AT)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::SavingSettlement.test_the_end_line_is_used_when_the_record_has_no_end
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: The end line is used when the record has no end.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_end_line_is_used_when_the_record_has_no_end(self) -> None:
#         (self.folder.path / "events.jsonl").write_text(json.dumps(
#             {"n": 1, "end": {"state": "cancelled", "at": AT.isoformat()}}) + "\n")
#         self.assertEqual(self.settle()[1]["settled"], "cancelled")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::SavingSettlement.test_without_an_end_or_a_timestamp_the_database_acceptance_time_is_used
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: Without an end or a timestamp the database acceptance time is used.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_without_an_end_or_a_timestamp_the_database_acceptance_time_is_used(self) -> None:
#         self.assertEqual(self.settle()[1]["settled"], "interrupted")
#         self.assertEqual(self.database.exchanges[X].ended_at, AT)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::SavingSettlement.test_an_exchange_that_already_ended_keeps_its_state_and_end_time
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: An exchange that already ended keeps its state and end time.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_an_exchange_that_already_ended_keeps_its_state_and_end_time(self) -> None:
#         existing = self.database.exchanges[X]
#         existing.state, existing.ended_at = "completed", AT
#         self.assertEqual(self.settle()[1]["settled"], "completed")
#         self.assertEqual((existing.state, existing.ended_at), ("completed", AT))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::SavingSettlement.test_a_failed_save_keeps_the_folder_for_another_settle
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: A failed save keeps the folder for another settle.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_failed_save_keeps_the_folder_for_another_settle(self) -> None:
#         self.database.fail_end = 1
#         status, answer = self.settle()
#         self.assertEqual(status, 1)
#         self.assertEqual(answer["error"]["code"], "database_unavailable")  # type: ignore[index]
#         self.assertTrue(self.folder.path.exists())
#
#         self.assertEqual(self.database.closed, 1)
#         self.assertEqual(self.database.exchanges[X].state, "open")
#         self.assertTrue(self.folder.path.exists())
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::SavingSettlement.test_a_replaced_exchange_recovers_only_runs_and_keeps_its_ended_state
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: A replaced exchange recovers only runs and keeps its ended state.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_replaced_exchange_recovers_only_runs_and_keeps_its_ended_state(self) -> None:
#         stored = self.database.exchanges[X]
#         stored.state, stored.ended_at, stored.replaced_by = "completed", AT, "replacement"
#         lines = [
#             {"n": 1, "event": {"type": "started", "runId": "run", "at": AT.isoformat()}},
#             {"n": 2, "event": {"type": "text", "runId": "run", "text": "discarded"}},
#             {"n": 3, "event": {"type": "tool_started", "runId": "run", "callId": "call", "name": "shell",
#                                 "input": {}, "at": AT.isoformat()}},
#             {"n": 4, "event": {"type": "usage", "runId": "run", "usage": {"inputTokens": 41},
#                                 "at": AT.isoformat()}},
#         ]
#         (self.folder.path / "events.jsonl").write_text("".join(json.dumps(line) + "\n" for line in lines))
#         self.assertEqual(self.settle(), (0, {"exchange": X, "settled": "completed"}))
#         self.assertEqual(self.database.messages, {})
#         self.assertEqual(self.database.tool_calls, {})
#         self.assertEqual(self.database.runs[(X, "run")]["usage"], {"inputTokens": 41})
#         self.assertEqual((stored.state, stored.ended_at, stored.replaced_by), ("completed", AT, "replacement"))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::SavingSettlement.test_a_settle_waiting_for_coordination_keeps_the_folder_and_respects_its_budget
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: A settle waiting for coordination keeps the folder and respects its budget.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_settle_waiting_for_coordination_keeps_the_folder_and_respects_its_budget(self) -> None:
#         async def blocked() -> None:
#             async with root_lock(self.exchanges, time.monotonic() + 1):
#                 with (mock.patch("arbol_trunk_trivial.settle.DATABASE_SECONDS", 0.03),
#                       self.assertRaises(Refusal) as caught):
#                     await settle_exchange(self.home, "rct", X, output=Output(), connect=self.database.connect())
#                 self.assertEqual(caught.exception.code, "database_unavailable")
#         asyncio.run(blocked())
#         self.assertTrue(self.folder.path.exists())
#         self.assertEqual(self.database.connections, 0)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_settle.py::SavingSettlement.test_an_unfinished_end_is_skipped_and_a_closed_failure_remains_unchanged
# Reason: Fake state/replay/default/refusal examples overlap unchanged top-tier concurrent settlers and retained real R13 recovery and R14 replacement scenarios. Case reviewed: An unfinished end is skipped and a closed failure remains unchanged.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_settle.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_an_unfinished_end_is_skipped_and_a_closed_failure_remains_unchanged(self) -> None:
#         stored = self.database.exchanges[X]
#         stored.state, stored.ended_at = "failed", AT
#         stored.error = {"code": "rate_limited", "message": "earlier failure", "retryAfterSeconds": 120}
#         before = copy.deepcopy(stored)
#         whole = {"n": 1, "event": {"type": "text", "runId": "run", "text": "whole", "at": AT.isoformat()}}
#         tail = {"n": 2, "end": {"state": "completed", "at": "2026-10-15T10:00:00Z"}}
#         (self.folder.path / "events.jsonl").write_bytes((json.dumps(whole) + "\n" + json.dumps(tail)).encode())
#         self.assertEqual(self.settle(), (0, {"exchange": X, "settled": "failed"}))
#         self.assertEqual(stored, before)
#         self.assertEqual(self.database.messages, {(X, 1): ("assistant", "whole")})
#         self.assertEqual(self.database.runs[(X, "run")]["outcome"], "interrupted")
#         self.assertEqual(self.database.runs[(X, "run")]["ended_at"], AT)
# LOW-TIER-SOURCE-END
# LOW-TIER-END
