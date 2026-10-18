"""Starting the one Driver run (TRV-0, "The request to the Driver"; RCT-0, "How a Trunk starts a Driver").

The route's `driver` names the launcher: `claude` starts `arbol-claude-driver`, `<driver>` starts
`arbol-<driver>-driver`. It is looked for only in the folders of the search path, so a `driver` with a `/` in it is
never found. It is started without `-v`, as `run --control --request <run-1.json>`, in the Trunk's own process group,
with its standard error and environment the Trunk's own. Its control input stays open; its output is read line by line,
however long a line is, and a line that is not an event is dropped.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

READ_SIZE = 65536
EXIT_POLL_SECONDS = 0.01


def launcher_name(driver: str) -> str:
    return f"arbol-{driver}-driver"


def find_launcher(driver: str, search_path: str | None = None) -> str | None:
    """The launcher of the Driver in the first folder of the search path that holds it, or None."""
    if not driver or "/" in driver or "\0" in driver:
        return None
    name = launcher_name(driver)
    folders = os.environ.get("PATH", "") if search_path is None else search_path
    for folder in folders.split(os.pathsep):
        if not folder:
            continue
        candidate = os.path.join(folder, name)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


@dataclass(frozen=True)
class Line:
    """One line of the Driver's output that is an event: its own text, without the newline, and its value."""

    text: str
    event: dict[str, Any]


def as_event(raw: bytes) -> Line | None:
    try:
        text = raw.decode("utf-8").rstrip("\r\n\t ")
        value = json.loads(text)
    except ValueError:
        return None
    if not isinstance(value, dict) or not isinstance(value.get("type"), str):
        return None
    return Line(text, value)


class Driver(Protocol):
    """What the loop needs of a Driver run: its output, its control input, and its process."""

    @property
    def returncode(self) -> int | None: ...

    @property
    def output_ended(self) -> bool: ...

    async def read(self, seconds: float) -> list[Line]: ...

    def write_control(self, line: str) -> None: ...

    def kill(self) -> None: ...


class DriverRun:
    """The Driver's process, its control input and its output."""

    def __init__(self, process: asyncio.subprocess.Process) -> None:
        self.process = process
        self._buffer = b""
        self._ended = False

    @classmethod
    async def start(cls, launcher: str, request_file: Path, working_folder: str) -> DriverRun:
        process = await asyncio.create_subprocess_exec(
            launcher, "run", "--control", "--request", str(request_file), cwd=working_folder,
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=None)
        return cls(process)

    @property
    def pid(self) -> int:
        return self.process.pid

    @property
    def returncode(self) -> int | None:
        """The exit status once the process has ended, whether or not its output is read to the end."""
        return self.process.returncode

    @property
    def output_ended(self) -> bool:
        return self._ended

    async def read(self, seconds: float) -> list[Line]:
        """The event lines that arrive within `seconds`. Once the output has ended, it waits at most `seconds` for the
        process to end, without waiting for its pipes, which a child of the Driver may still hold open."""
        assert self.process.stdout is not None
        if self._ended:
            await self._exit(seconds)
            return []
        try:
            chunk = await asyncio.wait_for(self.process.stdout.read(READ_SIZE), seconds)
        except TimeoutError:
            return []
        if not chunk:
            self._ended = True
            rest, self._buffer = self._buffer, b""
            line = as_event(rest) if rest.strip() else None
            return [line] if line else []
        self._buffer += chunk
        *whole, self._buffer = self._buffer.split(b"\n")
        return [line for line in (as_event(raw) for raw in whole) if line is not None]

    async def _exit(self, seconds: float) -> None:
        deadline = time.monotonic() + seconds
        while self.process.returncode is None and (remaining := deadline - time.monotonic()) > 0:
            await asyncio.sleep(min(remaining, EXIT_POLL_SECONDS))

    async def lines(self) -> AsyncIterator[Line]:
        """Every event line, until the output ends."""
        while not self._ended:
            for line in await self.read(3600):
                yield line

    def write_control(self, line: str) -> None:
        """Writes one line to the control input without waiting; what the Driver has not taken yet is kept."""
        if self.process.stdin is not None and not self.process.stdin.is_closing():
            self.process.stdin.write(line.encode("utf-8") + b"\n")

    def kill(self) -> None:
        """SIGKILL to the Driver's process, when it still lives."""
        if self.process.returncode is None:
            with contextlib.suppress(ProcessLookupError):
                self.process.kill()

    async def wait(self) -> int:
        return await self.process.wait()

    def close_control(self) -> None:
        if self.process.stdin is not None and not self.process.stdin.is_closing():
            self.process.stdin.close()
