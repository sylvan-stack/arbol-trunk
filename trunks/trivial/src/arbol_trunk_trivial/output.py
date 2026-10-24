"""Foreground output is a best-effort copy, never part of saving an Exchange (RCT-2.19)."""

from __future__ import annotations

import errno
import os
from collections.abc import Callable


class Output:
    """Write each line once without waiting; after a failed write leave standard output alone."""

    def __init__(self, write: Callable[[str], None] | None = None, *, descriptor: int = 1) -> None:
        self._write = write or (lambda text: _line(descriptor, text))
        self.broken = False

    def line(self, text: str) -> None:
        if self.broken:
            return
        try:
            self._write(text)
        except (OSError, ValueError):
            self.broken = True


def _line(descriptor: int, text: str) -> None:
    os.set_blocking(descriptor, False)
    data = (text + "\n").encode("utf-8", "surrogatepass")
    if os.write(descriptor, data) != len(data):
        raise OSError(errno.EIO, "Standard output did not take the whole line.")
