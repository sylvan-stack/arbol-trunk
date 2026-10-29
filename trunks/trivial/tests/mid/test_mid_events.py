"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_events as _support
# from test_events import (
#     Any,
#     EVENTS,
#     Events,
#     EventsFile,
#     Line,
#     Path,
#     json,
#     mock,
#     tempfile,
#     unittest,
# )


# class Events(_support.Events):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_events.py::Events.test_each_event_under_n_from_1_exactly_as_the_driver_wrote_it_and_the_end_last
#     def test_each_event_under_n_from_1_exactly_as_the_driver_wrote_it_and_the_end_last(self) -> None:
#         for raw in EVENTS:
#             line = as_event(raw)
#             assert line is not None
#             self.file.append_event(line)
#         self.assertEqual(self.file.append_end({"state": "completed", "at": "2026-10-15T09:30:11.050Z"}), 4)
#         lines = self.path.read_bytes().split(b"\n")
#         self.assertEqual(lines[-1], b"")
#         self.assertEqual(lines[:3], [b'{"n":%d,"event":%s}' % (n, raw) for n, raw in enumerate(EVENTS, 1)])
#         self.assertEqual(json.loads(lines[3]), {"n": 4, "end": {"state": "completed",
#                                                                 "at": "2026-10-15T09:30:11.050Z"}})
#         self.assertEqual([json.loads(line)["n"] for line in lines[:-1]], [1, 2, 3, 4])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_events.py::Events.test_each_event_under_n_from_1_exactly_as_the_driver_wrote_it_and_the_end_last

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_events.py::Events.test_each_line_is_one_write
#     def test_each_line_is_one_write(self) -> None:
#         line = as_event(EVENTS[0])
#         assert line is not None
#         with mock.patch("os.write", wraps=os.write) as write:
#             self.file.append_event(line)
#         self.assertEqual(write.call_count, 1)
#         self.assertTrue(write.call_args.args[1].endswith(b"\n"))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_events.py::Events.test_each_line_is_one_write

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_events.py::Events.test_tool_output_stops_after_one_mib_but_other_lines_and_calls_go_on_without_n_gaps
#     def test_tool_output_stops_after_one_mib_but_other_lines_and_calls_go_on_without_n_gaps(self) -> None:
#         def append(kind: str, run: str = "run", call: str = "call") -> int | None:
#             event = {"type": kind, "runId": run, "callId": call, "text": "x" * 40000}
#             return self.file.append_event(Line(json.dumps(event), event))
#
#         numbers = [append("tool_output_delta") for _ in range(60)]
#         self.assertIn(None, numbers)
#         self.assertIsNotNone(append("text"))
#         self.assertIsNotNone(append("tool_finished"))
#         self.assertIsNotNone(append("tool_output_delta", call="another"))
#         self.assertIsNotNone(append("tool_output_delta", run="another"))
#         raw = self.path.read_bytes().splitlines(keepends=True)
#         output = [line for line in raw if (event := json.loads(line)["event"])["type"] == "tool_output_delta"
#                   and event["runId"] == "run" and event["callId"] == "call"]
#         total = sum(map(len, output))
#         self.assertGreater(total, 1024 * 1024)
#         self.assertLessEqual(total, 1024 * 1024 + max(map(len, output)))
#         self.assertEqual([json.loads(line)["n"] for line in raw], list(range(1, len(raw) + 1)))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_events.py::Events.test_tool_output_stops_after_one_mib_but_other_lines_and_calls_go_on_without_n_gaps

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_events.py::Events.test_tool_output_counts_utf8_envelope_and_newline_bytes
#     def test_tool_output_counts_utf8_envelope_and_newline_bytes(self) -> None:
#         event = {"type": "tool_output_delta", "runId": "r", "callId": "c", "text": "😀" * 20}
#         line = Line(json.dumps(event, ensure_ascii=False), event)
#         with mock.patch("arbol_trunk_trivial.events.TOOL_OUTPUT_BYTES", 200):
#             self.assertEqual(self.file.append_event(line), 1)
#             self.assertEqual(self.file.append_event(line), 2)
#             self.assertIsNone(self.file.append_event(line))
#         data = self.path.read_bytes()
#         self.assertEqual(self.file.tool_bytes[("r", "c")], len(data))
#         self.assertGreater(len(data), 200)
#         self.assertEqual([json.loads(raw)["event"] for raw in data.splitlines()], [event, event])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_events.py::Events.test_tool_output_counts_utf8_envelope_and_newline_bytes

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_events.py::Events.test_an_answer_that_crosses_the_cap_sets_full_without_taking_an_n
#     def test_an_answer_that_crosses_the_cap_sets_full_without_taking_an_n(self) -> None:
#         with mock.patch("arbol_trunk_trivial.events.FILE_BYTES", 1):
#             self.assertIsNone(self.file.append_answer('{"type":"answer","askId":"q"}'))
#         self.assertTrue(self.file.full)
#         self.assertEqual(self.file.n, 0)
#         self.assertEqual(self.path.read_bytes(), b"")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_events.py::Events.test_an_answer_that_crosses_the_cap_sets_full_without_taking_an_n

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_events.py::Events.test_a_line_that_does_not_reach_the_file_whole_is_an_error
#     def test_a_line_that_does_not_reach_the_file_whole_is_an_error(self) -> None:
#         line = as_event(EVENTS[0])
#         assert line is not None
#         with mock.patch("os.write", return_value=3), self.assertRaises(OSError):
#             self.file.append_event(line)
#         self.assertEqual(self.file.n, 0)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_events.py::Events.test_a_line_that_does_not_reach_the_file_whole_is_an_error


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_events.py:2
# import os
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_events.py:2

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_events.py:9
# from arbol_trunk_trivial.driver import Line, as_event
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_events.py:9

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
