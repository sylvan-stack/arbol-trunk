import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from arbol_trunk_trivial.driver import Line, as_event
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

    def test_tool_output_stops_after_one_mib_but_other_lines_and_calls_go_on_without_n_gaps(self) -> None:
        def append(kind: str, run: str = "run", call: str = "call") -> int | None:
            event = {"type": kind, "runId": run, "callId": call, "text": "x" * 40000}
            return self.file.append_event(Line(json.dumps(event), event))

        numbers = [append("tool_output_delta") for _ in range(60)]
        self.assertIn(None, numbers)
        self.assertIsNotNone(append("text"))
        self.assertIsNotNone(append("tool_finished"))
        self.assertIsNotNone(append("tool_output_delta", call="another"))
        self.assertIsNotNone(append("tool_output_delta", run="another"))
        raw = self.path.read_bytes().splitlines(keepends=True)
        output = [line for line in raw if (event := json.loads(line)["event"])["type"] == "tool_output_delta"
                  and event["runId"] == "run" and event["callId"] == "call"]
        total = sum(map(len, output))
        self.assertGreater(total, 1024 * 1024)
        self.assertLessEqual(total, 1024 * 1024 + max(map(len, output)))
        self.assertEqual([json.loads(line)["n"] for line in raw], list(range(1, len(raw) + 1)))

    def test_tool_output_counts_utf8_envelope_and_newline_bytes(self) -> None:
        event = {"type": "tool_output_delta", "runId": "r", "callId": "c", "text": "😀" * 20}
        line = Line(json.dumps(event, ensure_ascii=False), event)
        with mock.patch("arbol_trunk_trivial.events.TOOL_OUTPUT_BYTES", 200):
            self.assertEqual(self.file.append_event(line), 1)
            self.assertEqual(self.file.append_event(line), 2)
            self.assertIsNone(self.file.append_event(line))
        data = self.path.read_bytes()
        self.assertEqual(self.file.tool_bytes[("r", "c")], len(data))
        self.assertGreater(len(data), 200)
        self.assertEqual([json.loads(raw)["event"] for raw in data.splitlines()], [event, event])

    def test_a_full_file_keeps_only_closures_of_written_starts_usage_finished_and_the_end(self) -> None:
        def append(kind: str, **fields: Any) -> int | None:
            value = {"type": kind, "runId": "r", **fields}
            return self.file.append_event(Line(json.dumps(value), value))

        append("tool_started", callId="kept")
        append("ask_opened", askId="kept-question", ask={"callId": "kept"})
        append("text", text="Already finished.")
        before = self.path.read_bytes()
        with mock.patch("arbol_trunk_trivial.events.FILE_BYTES", len(before)):
            self.assertIsNone(append("text", text="Would cross the cap."))
            self.assertTrue(self.file.full)
            for kind, fields in [("tool_started", {"callId": "omitted"}),
                                 ("ask_opened", {"askId": "omitted-question"}),
                                 ("tool_finished", {"callId": "omitted"}),
                                 ("ask_closed", {"askId": "omitted-question"}),
                                 ("tool_output_delta", {"callId": "kept", "text": "late"}),
                                 ("notice", {"message": "late"})]:
                self.assertIsNone(append(kind, **fields))
            self.assertIsNone(self.file.append_answer('{"type":"answer","askId":"kept-question"}'))
            self.assertEqual(self.path.read_bytes(), before)
            self.assertEqual(append("ask_closed", askId="kept-question"), 4)
            self.assertEqual(append("tool_finished", callId="kept", ok=False, interrupted=True), 5)
            self.assertEqual(append("usage", usage={"inputTokens": 8}), 6)
            self.assertEqual(append("finished", outcome="cancelled"), 7)
            self.assertEqual(self.file.append_end({"state": "failed", "error": {"code": "events_file_full"}}), 8)
        lines = [json.loads(line) for line in self.path.read_bytes().splitlines()]
        self.assertEqual([line["n"] for line in lines], list(range(1, 9)))
        self.assertEqual([line["event"]["type"] for line in lines[3:-1]],
                         ["ask_closed", "tool_finished", "usage", "finished"])
        self.assertEqual(self.file.bytes, self.path.stat().st_size)
        self.assertGreater(self.file.bytes, len(before))
        self.assertEqual(lines[-1]["end"]["error"]["code"], "events_file_full")

    def test_an_answer_that_crosses_the_cap_sets_full_without_taking_an_n(self) -> None:
        with mock.patch("arbol_trunk_trivial.events.FILE_BYTES", 1):
            self.assertIsNone(self.file.append_answer('{"type":"answer","askId":"q"}'))
        self.assertTrue(self.file.full)
        self.assertEqual(self.file.n, 0)
        self.assertEqual(self.path.read_bytes(), b"")

    def test_a_line_that_does_not_reach_the_file_whole_is_an_error(self) -> None:
        line = as_event(EVENTS[0])
        assert line is not None
        with mock.patch("os.write", return_value=3), self.assertRaises(OSError):
            self.file.append_event(line)
        self.assertEqual(self.file.n, 0)


if __name__ == "__main__":
    unittest.main()
