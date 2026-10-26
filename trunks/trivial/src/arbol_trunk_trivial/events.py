"""The answer as it arrives: `events.jsonl` (RCT-1).

One line for each event of the run, `{"n", "event"}`, with the event exactly as the Driver wrote it and `n` counting
from 1 without gaps; one line for each answer of `control` handed to the run, `{"n", "answer"}`, exactly as it was in
`control`; last, one line with the end. Only the Trunk writes the file, and each line is appended whole, with
one write, ending with a newline, before anything is saved from it.
"""

from __future__ import annotations

import errno
import json
import os
from pathlib import Path
from typing import Any

from .driver import Line
from .output import Output

TOOL_OUTPUT_BYTES = 1024 * 1024


class EventsFile:
    def __init__(self, path: Path, output: Output | None = None) -> None:
        self.path = path
        self.error: OSError | None = None
        try:
            self.descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
        except OSError as error:
            self.descriptor, self.error = -1, error
        self.n = 0
        self.output = output
        self.tool_bytes: dict[tuple[str, str], int] = {}

    def _append(self, data: bytes) -> None:
        if self.error is not None:
            return  # keep numbering the held lines; the caller saves their rows straight to the database
        try:
            written = os.write(self.descriptor, data)
            if written != len(data):
                raise OSError(errno.EIO, f"Only {written} of {len(data)} bytes of a line reached {self.path}.")
        except OSError as error:
            self.error = error
            raise
        if self.output is not None:
            self.output.line(data.decode("utf-8", "surrogatepass").removesuffix("\n"))

    def append_event(self, line: Line) -> int | None:
        """Append an event under the next n; omitted tool-output fragments take no number (RCT-1.12)."""
        output = line.event.get("type") == "tool_output_delta"
        key = (str(line.event.get("runId", "")), str(line.event.get("callId", "")))
        if output and self.tool_bytes.get(key, 0) > TOOL_OUTPUT_BYTES:
            return None
        n = self.n + 1
        data = b'{"n":%d,"event":%s}\n' % (n, line.text.encode("utf-8", "surrogatepass"))
        self._append(data)
        self.n = n
        if output and self.error is None:
            self.tool_bytes[key] = self.tool_bytes.get(key, 0) + len(data)
        return n

    def append_answer(self, text: str) -> int:
        """Appends an answer line of `control` that was handed to the run, exactly as it was there (RCT-1.11)."""
        n = self.n + 1
        self._append(b'{"n":%d,"answer":%s}\n' % (n, text.encode("utf-8", "surrogatepass")))
        self.n = n
        return n

    def append_end(self, end: dict[str, Any]) -> int:
        n = self.n + 1
        self._append(json.dumps({"n": n, "end": end}, ensure_ascii=False, separators=(",", ":"))
                     .encode("utf-8", "backslashreplace") + b"\n")
        self.n = n
        return n

    def close(self) -> None:
        if self.descriptor >= 0:
            os.close(self.descriptor)
            self.descriptor = -1
