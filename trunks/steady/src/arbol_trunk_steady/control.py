"""Stop and answers: `control` (RCT-1, "Stop and answers: control").

The Root manager appends `{"type":"stop"}` and the Arbol backend `{"type":"answer","askId",…,"answer",…}`, each as one
whole line with one write. The Trunk only reads the file, which it made empty with the folder: the lines that are new
since its last look, whole lines only, a last line without its newline kept until the rest of it is there. Each `stop`
and `answer` line is kept with its own text, so that it is handed on unchanged (RCT-1.7) and an answer is appended to
`events.jsonl` exactly as it was (RCT-1.11). Every other line is ignored.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

KINDS = ("stop", "answer")
READ_SIZE = 65536
ROUND_LIMIT = 1024 * 1024  # what one look reads at most; the rest waits for the next round


@dataclass(frozen=True)
class ControlLine:
    """A `stop` or an `answer` line of `control`: its own text, without the newline, and its value."""

    text: str
    value: dict[str, Any]

    @property
    def kind(self) -> str:
        return str(self.value["type"])


def _no_constant(name: str) -> NoReturn:
    raise ValueError(f"{name} is no JSON value.")


def as_control(raw: bytes) -> ControlLine | None:
    """The line as a `stop` or an `answer` line, or None for a line the Trunk does not know."""
    try:
        text = raw.decode("utf-8")
        value = json.loads(text, parse_constant=_no_constant)
    except ValueError:
        return None
    if not isinstance(value, dict) or value.get("type") not in KINDS:
        return None
    return ControlLine(text, value)


class ControlFile:
    """The Exchange's `control`, opened for reading only."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.descriptor = os.open(path, os.O_RDONLY)
        self._buffer = b""

    def read(self) -> list[ControlLine]:
        """The `stop` and `answer` lines that are new and whole since the last look, in order."""
        taken = 0
        while taken < ROUND_LIMIT:
            chunk = os.read(self.descriptor, READ_SIZE)
            if not chunk:
                break
            taken += len(chunk)
            self._buffer += chunk
        *whole, self._buffer = self._buffer.split(b"\n")
        return [line for line in (as_control(raw) for raw in whole) if line is not None]

    def close(self) -> None:
        if self.descriptor >= 0:
            os.close(self.descriptor)
            self.descriptor = -1
