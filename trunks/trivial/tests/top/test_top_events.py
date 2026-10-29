"""Individually selected top-tier cases. Shared fixtures retain their original paths."""
from __future__ import annotations

import test_events as _support
from test_events import (
    Any,
    Line,
    json,
    mock,
)


class Events(_support.Events):
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
