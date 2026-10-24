import json
import os
import tempfile
import time
import unittest
from pathlib import Path

from arbol_trunk_trivial.driver import as_event
from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.output import Output


class ForegroundOutput(unittest.TestCase):
    def test_a_pipe_that_nothing_reads_never_holds_up_the_writer(self) -> None:
        reader, writer = os.pipe()
        self.addCleanup(os.close, reader)
        self.addCleanup(os.close, writer)
        output = Output(descriptor=writer)
        began = time.monotonic()
        for _ in range(10000):
            output.line("x" * 1000)
        self.assertLess(time.monotonic() - began, 0.5)
        self.assertTrue(output.broken)

    def test_a_closed_pipe_stops_output_and_does_not_stop_the_events_file(self) -> None:
        reader, writer = os.pipe()
        os.close(reader)
        self.addCleanup(os.close, writer)
        output = Output(descriptor=writer)
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "events.jsonl"
            path.touch()
            events = EventsFile(path, output)
            try:
                event = as_event(b'{"type":"text","text":"hello"}')
                assert event is not None
                events.append_event(event)
                events.append_end({"state": "completed"})
            finally:
                events.close()
            self.assertTrue(output.broken)
            self.assertEqual(len(path.read_text().splitlines()), 2)
            self.assertEqual(json.loads(path.read_text().splitlines()[-1])["end"]["state"], "completed")

    def test_every_kind_of_line_is_copied_after_it_reaches_the_file(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "events.jsonl"
            path.touch()
            copied: list[str] = []

            def copy(text: str) -> None:
                self.assertEqual(path.read_text().splitlines()[-1], text)
                copied.append(text)

            events = EventsFile(path, Output(copy))
            try:
                event = as_event(b'{ "type": "text", "text": "hello" }')
                assert event is not None
                events.append_event(event)
                events.append_answer('{"type":"answer","askId":"a","answer":{"type":"decline"}}')
                events.append_end({"state": "cancelled"})
            finally:
                events.close()
            self.assertEqual(copied, path.read_text().splitlines())
