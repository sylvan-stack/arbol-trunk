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
import signal
import time
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

READ_SIZE = 65536
EXIT_POLL_SECONDS = 0.01
CAPABILITY_SECONDS = 5.0
CAPABILITY_BYTES = 256 * 1024


class CapabilityError(Exception):
    """The selected route cannot safely start inference."""


class CapabilityStopped(Exception):
    """The caller stopped while capability queries were running."""


def migration_ready(home: Path, driver: str, subscription: str | None) -> None:
    path = home / ".arbol/pi-cutover.json"
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return
    except OSError:
        raise CapabilityError(
            "The Pi migration marker cannot be read; finish or explicitly restore the migration.") from None
    try:
        if len(raw) > CAPABILITY_BYTES:
            raise ValueError
        marker = json.loads(raw)
        if not isinstance(marker, dict) or marker.get("phase") not in {
            "preparing", "quiesced", "publishing", "verifying", "complete", "restoring", "restored"
        } or not isinstance(marker.get("blockedRoutes"), list):
            raise ValueError
        for route in marker["blockedRoutes"]:
            if (not isinstance(route, dict) or not isinstance(route.get("driver"), str)
                    or not (route.get("subscription") is None or isinstance(route["subscription"], str))):
                raise ValueError
        if marker["phase"] in {"complete", "restored"}:
            return
        if any(route["driver"] == driver and
               (route.get("subscription") is None or subscription is None or route["subscription"] == subscription)
               for route in marker["blockedRoutes"]):
            raise CapabilityError("This route is paused by the Pi migration; finish or explicitly restore it.")
    except (ValueError, TypeError):
        raise CapabilityError("The Pi migration marker is invalid; repair or explicitly restore it.") from None


async def capability_query(launcher: str, arguments: list[str], cwd: str, stopped: Callable[[], bool]) -> Any:
    if stopped():
        raise CapabilityStopped
    process = await asyncio.create_subprocess_exec(
        launcher, *arguments, cwd=cwd, stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL, start_new_session=True)

    async def collect() -> bytes:
        assert process.stdout is not None
        data = bytearray()
        while chunk := await process.stdout.read(READ_SIZE):
            data.extend(chunk)
            if len(data) > CAPABILITY_BYTES:
                raise CapabilityError("Driver capability output exceeds its bound.")
        if await process.wait() != 0:
            raise CapabilityError("Driver capability query failed; check its settings and selected Subscription.")
        return bytes(data)

    task = asyncio.create_task(collect())
    deadline = time.monotonic() + CAPABILITY_SECONDS
    try:
        while not task.done():
            if stopped():
                raise CapabilityStopped
            if time.monotonic() >= deadline:
                raise CapabilityError("Driver capability query timed out.")
            await asyncio.wait({task}, timeout=0.02)
        try:
            return json.loads(task.result())
        except (ValueError, UnicodeError):
            raise CapabilityError("Driver capability query returned invalid JSON.") from None
    finally:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await process.wait()


async def capabilities(launcher: str, driver: str, subscription: str | None, cwd: str, home: Path,
                       stopped: Callable[[], bool]) -> None:
    migration_ready(home, driver, subscription)
    info = await capability_query(launcher, ["info"], cwd, stopped)
    if (not isinstance(info, dict) or info.get("driver") != driver
            or type(info.get("contract")) is not int or info["contract"] not in (1, 2)):
        raise CapabilityError("The launcher does not offer the selected Driver and a supported contract (1 or 2).")
    families = await capability_query(launcher, ["subscriptions", "families"], cwd, stopped)
    records = await capability_query(launcher, ["subscriptions", "list"], cwd, stopped)
    if (not isinstance(families, list) or not families or not isinstance(records, list) or not records
            or any(not isinstance(item, dict) or not isinstance(item.get("id"), str) for item in families)
            or any(not isinstance(item, dict) or not isinstance(item.get("id"), str)
                   or not isinstance(item.get("family"), str) for item in records)):
        raise CapabilityError("The Driver returned invalid family or Subscription capabilities.")
    offered = {item["id"] for item in families}
    selected = [item for item in records if subscription is None or item["id"] == subscription]
    if not selected or any(item["family"] not in offered for item in selected):
        raise CapabilityError("The selected Subscription is unavailable; migrate retired Claude z.ai routes to Pi.")
    migration_ready(home, driver, subscription)
    if stopped():
        raise CapabilityStopped


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

    def write_control(self, line: str) -> bool: ...

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

    def write_control(self, line: str) -> bool:
        """Writes one line to the control input without waiting; what the Driver has not taken yet is kept. False when
        the control input is closed, and the line was not handed on."""
        if self.process.stdin is None or self.process.stdin.is_closing():
            return False
        self.process.stdin.write(line.encode("utf-8") + b"\n")
        return True

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
