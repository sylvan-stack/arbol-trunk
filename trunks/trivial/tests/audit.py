"""The files a piece of the Trunk opens, through Python's audit hook for `open` (builtins.open and os.open)."""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

_listening: list[list[str]] = []


def _hook(event: str, args: tuple[Any, ...]) -> None:
    if event == "open" and _listening and args[0] is not None and not isinstance(args[0], int):
        _listening[-1].append(os.fsdecode(args[0]))


sys.addaudithook(_hook)


@contextmanager
def opened_files() -> Iterator[list[str]]:
    files: list[str] = []
    _listening.append(files)
    try:
        yield files
    finally:
        _listening.pop()
