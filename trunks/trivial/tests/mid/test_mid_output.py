"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_output as _support
from test_output import (Output ,mock ,os ,signal)


class ForegroundOutput(_support.ForegroundOutput):


# TEST-TIER-BEGIN trunks/trivial/tests/test_output.py::ForegroundOutput.test_a_termination_signal_is_delivered_only_after_shared_descriptor_flags_are_restored
    def test_a_termination_signal_is_delivered_only_after_shared_descriptor_flags_are_restored(self) -> None:
        reader, writer = os.pipe()
        self.addCleanup(os.close, reader)
        self.addCleanup(os.close, writer)
        seen: list[bool] = []
        old_handler = signal.signal(signal.SIGTERM, lambda *_args: seen.append(os.get_blocking(writer)))
        self.addCleanup(signal.signal, signal.SIGTERM, old_handler)
        write = os.write

        def interrupted(descriptor: int, data: bytes) -> int:
            os.kill(os.getpid(), signal.SIGTERM)
            return write(descriptor, data)

        with mock.patch("arbol_trunk_trivial.output.os.write", side_effect=interrupted):
            Output(descriptor=writer).line("hello")
        self.assertEqual(seen, [True])
        self.assertEqual(os.read(reader, 6), b"hello\n")
# TEST-TIER-END trunks/trivial/tests/test_output.py::ForegroundOutput.test_a_termination_signal_is_delivered_only_after_shared_descriptor_flags_are_restored

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_output.py::ForegroundOutput.test_a_pipe_that_nothing_reads_never_holds_up_the_writer
# Reason: Ordinary unread/closed-pipe copies overlap real R2 foreground behavior; retain the distinct real-signal descriptor restoration window. Case reviewed: A pipe that nothing reads never holds up the writer.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_output.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_output.py::ForegroundOutput.test_a_closed_pipe_stops_output_and_does_not_stop_the_events_file
# Reason: Ordinary unread/closed-pipe copies overlap real R2 foreground behavior; retain the distinct real-signal descriptor restoration window. Case reviewed: A closed pipe stops output and does not stop the events file.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_output.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_output.py::ForegroundOutput.test_every_kind_of_line_is_copied_after_it_reaches_the_file
# Reason: Ordinary unread/closed-pipe copies overlap real R2 foreground behavior; retain the distinct real-signal descriptor restoration window. Case reviewed: Every kind of line is copied after it reaches the file.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_output.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END
