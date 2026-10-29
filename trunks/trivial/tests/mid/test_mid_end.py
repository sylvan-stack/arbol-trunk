
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_end.py::Ends.test_the_state_is_the_runs_outcome
# Reason: Simple end-state mappings and synthetic retry counts overlap actual contract cancellation, outage and recovery scenarios. Case reviewed: The state is the runs outcome.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_end.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_state_is_the_runs_outcome(self) -> None:
#         self.assertEqual((end_of_run({"outcome": "completed"}).state, end_of_run({"outcome": "completed"}).error),
#                          ("completed", None))
#         self.assertEqual(end_of_run({"outcome": "cancelled"}).exit_status, 2)
#         failed = end_of_run({"outcome": "failed", "error": RATE})
#         self.assertEqual((failed.state, failed.error, failed.exit_status), ("failed", RATE, 1))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_end.py::Ends.test_without_a_finished_event_the_exchange_fails_with_driver_failed
# Reason: Simple end-state mappings and synthetic retry counts overlap actual contract cancellation, outage and recovery scenarios. Case reviewed: Without a finished event the exchange fails with driver failed.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_end.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_without_a_finished_event_the_exchange_fails_with_driver_failed(self) -> None:
#         end = end_of_run(None)
#         self.assertEqual(end.state, "failed")
#         assert end.error is not None
#         self.assertEqual(end.error["code"], "driver_failed")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_end.py::Ends.test_the_end_is_the_last_line_and_the_same_end_is_in_the_record
# Reason: Simple end-state mappings and synthetic retry counts overlap actual contract cancellation, outage and recovery scenarios. Case reviewed: The end is the last line and the same end is in the record.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_end.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_end_is_the_last_line_and_the_same_end_is_in_the_record(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             folder = ExchangeFolder.make(Path(name), X, {"exchange": X, "signsOfLife": {}})
#             events = EventsFile(folder.path / "events.jsonl")
#             self.addCleanup(events.close)
#             end = end_of_run({"outcome": "failed", "error": RATE})
#             write_end(events, folder, end)
#             lines = (folder.path / "events.jsonl").read_text().splitlines()
#             self.assertEqual(json.loads(lines[-1]), {"n": 1, "end": end.value()})
#             self.assertEqual(json.loads((folder.path / "record.json").read_text())["end"], end.value())
#             self.assertEqual(set(end.value()), {"state", "at", "error"})
#             self.assertNotIn("error", End("completed", end.at).value())
#             self.assertEqual(sorted(os.listdir(folder.path)), ["control", "events.jsonl", "record.json"])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_end.py::SavingTheEnd.test_the_rows_not_yet_saved_and_the_final_state_in_one_transaction_then_the_folder_goes
# Reason: Simple end-state mappings and synthetic retry counts overlap actual contract cancellation, outage and recovery scenarios. Case reviewed: The rows not yet saved and the final state in one transaction then the folder goes.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_end.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_rows_not_yet_saved_and_the_final_state_in_one_transaction_then_the_folder_goes(self) -> None:
#         run = RunRow(X, f"{X}.1", "agent", "completed", {}, None, None, datetime.now(UTC))
#         end = End("completed", datetime.now(UTC))
#         self.assertTrue(self.finish([MessageRow(X, 3, "a")], [run], end))
#         self.assertEqual(self.database.ends, 1)
#         self.assertEqual(self.database.messages[(X, 3)], ("assistant", "a"))
#         self.assertIn((X, f"{X}.1"), self.database.runs)
#         self.assertEqual((self.database.exchanges[X].state, self.database.exchanges[X].ended_at), ("completed", end.at))
#         self.assertEqual(os.listdir(self.exchanges), [])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_end.py::SavingTheEnd.test_an_exchange_that_has_ended_is_not_changed
# Reason: Simple end-state mappings and synthetic retry counts overlap actual contract cancellation, outage and recovery scenarios. Case reviewed: An exchange that has ended is not changed.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_end.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_an_exchange_that_has_ended_is_not_changed(self) -> None:
#         self.database.exchanges[X].state = "interrupted"
#         self.assertTrue(self.finish([], [], End("failed", datetime.now(UTC), RATE)))
#         self.assertEqual((self.database.exchanges[X].state, self.database.exchanges[X].error), ("interrupted", None))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_end.py::SavingTheEnd.test_a_database_that_is_away_is_tried_for_60_seconds_and_then_the_folder_stays
# Reason: Simple end-state mappings and synthetic retry counts overlap actual contract cancellation, outage and recovery scenarios. Case reviewed: A database that is away is tried for 60 seconds and then the folder stays.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_end.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_database_that_is_away_is_tried_for_60_seconds_and_then_the_folder_stays(self) -> None:
#         self.database.fail_end = 1000
#         began = time.monotonic()
#         with mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "100"}):
#             self.assertFalse(self.finish([], [], End("completed", datetime.now(UTC))))
#         self.assertGreater(time.monotonic() - began, 0.5)
#         self.assertLess(time.monotonic() - began, 3)
#         self.assertGreaterEqual(self.database.connections, 10)
#         self.assertEqual(os.listdir(self.exchanges), [X])
#         self.assertEqual(self.database.exchanges[X].state, "open")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_end.py::SavingTheEnd.test_the_last_tries_stop_at_sixty_scaled_seconds_on_a_moved_clock
# Reason: Simple end-state mappings and synthetic retry counts overlap actual contract cancellation, outage and recovery scenarios. Case reviewed: The last tries stop at sixty scaled seconds on a moved clock.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_end.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_last_tries_stop_at_sixty_scaled_seconds_on_a_moved_clock(self) -> None:
#         clock = MovedClock()
#         self.database.fail_end = 1000
#         waits: list[float] = []
#
#         async def advance(seconds: float) -> None:
#             waits.append(seconds)
#             clock.t += seconds
#
#         with mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "10"}), \
#                 mock.patch("arbol_trunk_trivial.end.uptime", clock.now), \
#                 mock.patch("arbol_trunk_trivial.end.asyncio.sleep", advance):
#             self.assertFalse(self.finish([], [], End("completed", datetime.now(UTC))))
#         self.assertEqual(waits, [0.5] * 12)
#         self.assertEqual(clock.since_start(), 6)
#         self.assertEqual(self.database.connections, 13)
#         self.assertEqual(self.database.closed, 13)
#         self.assertTrue(self.folder.path.exists())
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_end.py::SavingTheEnd.test_a_database_back_within_the_60_seconds_takes_the_end
# Reason: Simple end-state mappings and synthetic retry counts overlap actual contract cancellation, outage and recovery scenarios. Case reviewed: A database back within the 60 seconds takes the end.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_end.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_database_back_within_the_60_seconds_takes_the_end(self) -> None:
#         self.database.fail_end = 2
#         with mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "100"}):
#             self.assertTrue(self.finish([], [], End("completed", datetime.now(UTC))))
#         self.assertEqual(self.database.exchanges[X].state, "completed")
# LOW-TIER-SOURCE-END
# LOW-TIER-END
