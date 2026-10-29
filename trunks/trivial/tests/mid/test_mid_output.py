"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_output as _support
# from test_output import (
#     ForegroundOutput,
#     unittest,
# )


# class ForegroundOutput(_support.ForegroundOutput):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_output.py::ForegroundOutput.test_a_pipe_that_nothing_reads_never_holds_up_the_writer
#     def test_a_pipe_that_nothing_reads_never_holds_up_the_writer(self) -> None:
#         reader, writer = os.pipe()
#         self.addCleanup(os.close, reader)
#         self.addCleanup(os.close, writer)
#         output = Output(descriptor=writer)
#         began = time.monotonic()
#         for _ in range(10000):
#             output.line("x" * 1000)
#         self.assertLess(time.monotonic() - began, 0.5)
#         self.assertTrue(output.broken)
#         self.assertTrue(os.get_blocking(writer))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_output.py::ForegroundOutput.test_a_pipe_that_nothing_reads_never_holds_up_the_writer

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_output.py::ForegroundOutput.test_a_closed_pipe_stops_output_and_does_not_stop_the_events_file
#     def test_a_closed_pipe_stops_output_and_does_not_stop_the_events_file(self) -> None:
#         reader, writer = os.pipe()
#         os.close(reader)
#         self.addCleanup(os.close, writer)
#         output = Output(descriptor=writer)
#         with tempfile.TemporaryDirectory() as name:
#             path = Path(name) / "events.jsonl"
#             path.touch()
#             events = EventsFile(path, output)
#             try:
#                 event = as_event(b'{"type":"text","text":"hello"}')
#                 assert event is not None
#                 events.append_event(event)
#                 events.append_end({"state": "completed"})
#             finally:
#                 events.close()
#             self.assertTrue(output.broken)
#             self.assertTrue(os.get_blocking(writer))
#             self.assertEqual(len(path.read_text().splitlines()), 2)
#             self.assertEqual(json.loads(path.read_text().splitlines()[-1])["end"]["state"], "completed")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_output.py::ForegroundOutput.test_a_closed_pipe_stops_output_and_does_not_stop_the_events_file

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_output.py::ForegroundOutput.test_every_kind_of_line_is_copied_after_it_reaches_the_file
#     def test_every_kind_of_line_is_copied_after_it_reaches_the_file(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             path = Path(name) / "events.jsonl"
#             path.touch()
#             copied: list[str] = []
#
#             def copy(text: str) -> None:
#                 self.assertEqual(path.read_text().splitlines()[-1], text)
#                 copied.append(text)
#
#             events = EventsFile(path, Output(copy))
#             try:
#                 event = as_event(b'{ "type": "text", "text": "hello" }')
#                 assert event is not None
#                 events.append_event(event)
#                 events.append_answer('{"type":"answer","askId":"a","answer":{"type":"decline"}}')
#                 events.append_end({"state": "cancelled"})
#             finally:
#                 events.close()
#             self.assertEqual(copied, path.read_text().splitlines())
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_output.py::ForegroundOutput.test_every_kind_of_line_is_copied_after_it_reaches_the_file

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_output.py::ForegroundOutput.test_a_termination_signal_is_delivered_only_after_shared_descriptor_flags_are_restored
#     def test_a_termination_signal_is_delivered_only_after_shared_descriptor_flags_are_restored(self) -> None:
#         reader, writer = os.pipe()
#         self.addCleanup(os.close, reader)
#         self.addCleanup(os.close, writer)
#         seen: list[bool] = []
#         old_handler = signal.signal(signal.SIGTERM, lambda *_args: seen.append(os.get_blocking(writer)))
#         self.addCleanup(signal.signal, signal.SIGTERM, old_handler)
#         write = os.write
#
#         def interrupted(descriptor: int, data: bytes) -> int:
#             os.kill(os.getpid(), signal.SIGTERM)
#             return write(descriptor, data)
#
#         with mock.patch("arbol_trunk_trivial.output.os.write", side_effect=interrupted):
#             Output(descriptor=writer).line("hello")
#         self.assertEqual(seen, [True])
#         self.assertEqual(os.read(reader, 6), b"hello\n")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_output.py::ForegroundOutput.test_a_termination_signal_is_delivered_only_after_shared_descriptor_flags_are_restored


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_output.py:1
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_output.py:1

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_output.py:2
# import os
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_output.py:2

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_output.py:3
# import signal
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_output.py:3

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_output.py:4
# import tempfile
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_output.py:4

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_output.py:5
# import time
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_output.py:5

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_output.py:7
# from pathlib import Path
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_output.py:7

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_output.py:8
# from unittest import mock
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_output.py:8

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_output.py:10
# from arbol_trunk_trivial.driver import as_event
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_output.py:10

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_output.py:11
# from arbol_trunk_trivial.events import EventsFile
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_output.py:11

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_output.py:12
# from arbol_trunk_trivial.output import Output
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_output.py:12

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
