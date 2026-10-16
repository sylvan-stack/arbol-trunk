"""The answer as it arrives: `events.jsonl` (RCT-1).

One line for each event of the run, `{"n", "event"}`, with the event exactly as the Driver wrote it and `n` counting
from 1 without gaps; last, one line with the end. Only the Trunk writes the file, and each line is appended whole, with
one write, ending with a newline, before anything is saved from it.
"""

from __future__ import annotations

import errno
import json
import os
from pathlib import Path
from typing import Any

from .driver import Line


class EventsFile:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
        self.n = 0

    def _append(self, data: bytes) -> None:
        written = os.write(self.descriptor, data)
        if written != len(data):
            raise OSError(errno.EIO, f"Only {written} of {len(data)} bytes of a line reached {self.path}.")

    def append_event(self, line: Line) -> int:
        """Appends the event under the next `n`, and gives that `n`."""
        n = self.n + 1
        self._append(b'{"n":%d,"event":%s}\n' % (n, line.text.encode("utf-8", "surrogatepass")))
        self.n = n
        return n

    def append_end(self, end: dict[str, Any]) -> int:
        n = self.n + 1
        self._append(json.dumps({"n": n, "end": end}, ensure_ascii=False, separators=(",", ":"))
                     .encode("utf-8", "surrogatepass") + b"\n")
        self.n = n
        return n

    def close(self) -> None:
        if self.descriptor >= 0:
            os.close(self.descriptor)
            self.descriptor = -1
