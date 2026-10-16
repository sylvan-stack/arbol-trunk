import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from arbol_trunk_trivial.driver import as_event
from arbol_trunk_trivial.events import EventsFile

EVENTS = [
    b'{"runId":"x.1","seq":1,"at":"2026-10-15T09:30:01.204Z","type":"started","continuity":"fresh"}',
    b'{"runId":"x.1","seq":2,"type":"text_delta","text":"Let me "}',
    b'{"type": "text", "runId": "x.1", "seq": 3, "text": "Let me read it. \\ud83d"}',
]


class Events(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "events.jsonl"
        self.path.write_bytes(b"")
        self.file = EventsFile(self.path)
        self.addCleanup(self.file.close)

    def test_each_event_under_n_from_1_exactly_as_the_driver_wrote_it_and_the_end_last(self) -> None:
        for raw in EVENTS:
            line = as_event(raw)
            assert line is not None
            self.file.append_event(line)
        self.assertEqual(self.file.append_end({"state": "completed", "at": "2026-10-15T09:30:11.050Z"}), 4)
        lines = self.path.read_bytes().split(b"\n")
        self.assertEqual(lines[-1], b"")
        self.assertEqual(lines[:3], [b'{"n":%d,"event":%s}' % (n, raw) for n, raw in enumerate(EVENTS, 1)])
        self.assertEqual(json.loads(lines[3]), {"n": 4, "end": {"state": "completed",
                                                                "at": "2026-10-15T09:30:11.050Z"}})
        self.assertEqual([json.loads(line)["n"] for line in lines[:-1]], [1, 2, 3, 4])

    def test_each_line_is_one_write(self) -> None:
        line = as_event(EVENTS[0])
        assert line is not None
        with mock.patch("os.write", wraps=os.write) as write:
            self.file.append_event(line)
        self.assertEqual(write.call_count, 1)
        self.assertTrue(write.call_args.args[1].endswith(b"\n"))

    def test_a_line_that_does_not_reach_the_file_whole_is_an_error(self) -> None:
        line = as_event(EVENTS[0])
        assert line is not None
        with mock.patch("os.write", return_value=3), self.assertRaises(OSError):
            self.file.append_event(line)
        self.assertEqual(self.file.n, 0)


if __name__ == "__main__":
    unittest.main()
