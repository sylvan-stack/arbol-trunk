# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""A whole Exchange, from the message to its end, with a stand-in launcher and the fake database: no database server,
no Driver and no network."""

from audit import opened_files
from fakes import FakeConnection, FakeDatabase
from arbol_trunk_trivial.database import RowRejected
from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.rows import MessageRow, Row
from arbol_trunk_trivial.settings import settings_file


import asyncio
import json
import os
import tempfile
import time
import unittest
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any
from unittest import mock

from fakes import FakeDatabase
from stand_ins import security_stand_in, with_capabilities

from arbol_trunk_trivial.command import handed, parse
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.run import Output, run_exchange
from arbol_trunk_trivial.start import prepare

CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"
FIRST = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
SECOND = "2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"

# The stand-in launcher: it keeps what it was started with and the record beside its request, and plays the events
# of the file named in $STANDIN_EVENTS, with its runId.
LAUNCHER = """#!/bin/sh
log="$STANDIN_LOG"
printf '%s\\n' "$*" >> "$log/starts"
request="$4"
cp "$request" "$log/request-$(wc -l < "$log/starts" | tr -d ' ').json"
cp "$(dirname "$request")/record.json" "$log/record.json"
run=$(sed -n 's/.*"runId":"\\([^"]*\\)".*/\\1/p' "$request")
sed "s/RUN/$run/g" "$STANDIN_EVENTS"
"""

PLAIN = [
    {"runId": "RUN", "seq": 1, "at": "2026-10-15T09:30:01.204Z", "type": "started", "continuity": "fresh",
     "subscriptionId": "anthropic", "model": "sonnet", "toolVersion": "stand-in", "driverBuild": "0"},
    {"runId": "RUN", "seq": 2, "at": "2026-10-15T09:30:03.020Z", "type": "text_delta", "text": "Let me "},
    {"runId": "RUN", "seq": 3, "at": "2026-10-15T09:30:03.310Z", "type": "text", "text": "Let me read it."},
    {"runId": "RUN", "seq": 4, "at": "2026-10-15T09:30:03.400Z", "type": "tool_started", "callId": "call_1",
     "name": "shell", "input": {"command": "cat build.sh"}},
    {"runId": "RUN", "seq": 5, "at": "2026-10-15T09:30:03.900Z", "type": "tool_finished", "callId": "call_1",
     "ok": True, "result": {"output": "#!/bin/sh\n", "exitCode": 0}},
    {"runId": "RUN", "seq": 6, "at": "2026-10-15T09:30:09.700Z", "type": "text", "text": "It sets -e."},
    {"runId": "RUN", "seq": 7, "at": "2026-10-15T09:30:09.800Z", "type": "finished", "outcome": "completed",
     "usage": {"model": "sonnet", "inputTokens": 5120, "outputTokens": 812}, "producedOutput": True,
     "unfinishedCalls": []},
]

# A launcher that starts a shell call and waits for a line on its control input; on a stop line it finishes the call as
# interrupted and the run as cancelled, as a Driver does (DRV-2), and keeps the line it got.
STOPPABLE = """#!/bin/sh
run=$(sed -n 's/.*"runId":"\\([^"]*\\)".*/\\1/p' "$4")
printf '%s\\n' '{"runId":"'"$run"'","seq":1,"type":"started","continuity":"fresh","subscriptionId":"s","toolVersion":"t","driverBuild":"0"}'
printf '%s\\n' '{"runId":"'"$run"'","seq":2,"type":"tool_started","callId":"call_1","name":"shell","input":{"command":"make"}}'
IFS= read -r line
printf '%s\\n' "$line" > "$STANDIN_LOG/control"
printf '%s\\n' '{"runId":"'"$run"'","seq":3,"type":"tool_finished","callId":"call_1","ok":false,"error":"Stopped.","interrupted":true}'
printf '%s\\n' '{"runId":"'"$run"'","seq":4,"type":"finished","outcome":"cancelled","producedOutput":false,"unfinishedCalls":[]}'
"""


class WholeExchange(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(os.path.realpath(folder.name))
        self.root = roots_folder(self.home) / "rct"
        (self.root / "exchanges").mkdir(parents=True)
        (self.root / "root.json").write_text(json.dumps({"database": "arbol_rct", "rootContract": 1}))
        (self.home / ".arbol").mkdir()
        (self.home / ".arbol" / "database.json").write_text(json.dumps({"address": "postgresql://rct@%2Ftmp%2Fx"}))
        self.security = str(security_stand_in(self.home, status=44))
        self.bin = self.home / "bin"
        self.bin.mkdir()
        (self.bin / "arbol-claude-driver").write_text(with_capabilities(LAUNCHER))
        os.chmod(self.bin / "arbol-claude-driver", 0o755)
        self.log = self.home / "log"
        self.log.mkdir()
        self.work = self.home / "work"
        self.work.mkdir()
        self.database = FakeDatabase()
        self.events(PLAIN)

    def events(self, events: list[dict[str, Any]]) -> None:
        (self.log / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))


    def run_trunk(self, *args: str, small: dict[str, str] | None = None,
                  during: Callable[[], Awaitable[None]] | None = None) -> tuple[int, list[str]]:
        """Runs `run` to its end; `during` runs beside it, from its start."""
        lines: list[str] = []
        request = {"smallCallRoute": small} if small else {}
        file = self.home / "start.json"
        file.write_text(json.dumps(request))
        environment = {"STANDIN_LOG": str(self.log), "STANDIN_EVENTS": str(self.log / "events.jsonl"),
                       "ARBOL_TEST_TIME_SCALE": "10"}
        with mock.patch.dict("os.environ", environment):
            prepared = prepare(handed(parse(["--root", "rct", "run", "--request", str(file), *args]),
                                      started_in=str(self.work)), self.home, self.security)

            async def go() -> int:
                beside = asyncio.ensure_future(during()) if during is not None else None
                status = await run_exchange(
                    prepared, self.database.connect(), build="0", process={"pid": 1, "startedAt": "x"},
                    started=time.monotonic(), output=Output(lines.append), search_path=f"{self.bin}:/usr/bin:/bin")
                if beside is not None:
                    await beside
                return status

            status = asyncio.run(go())
        return status, lines

    def stop_when_the_folder_is_there(self, exchange: str) -> Callable[[], Awaitable[None]]:
        """Appends a stop line to the Exchange's `control` as soon as it is in place, as a writer does (RCT-1.8)."""
        control = self.root / "exchanges" / exchange / "control"

        async def stop() -> None:
            while not control.exists():
                await asyncio.sleep(0.005)
            descriptor = os.open(control, os.O_WRONLY | os.O_APPEND)
            try:
                os.write(descriptor, b'{"type":"stop"}\n')
            finally:
                os.close(descriptor)

        return stop


# Archived complete imports; restore needed names in their original scope, not at this file tail.
