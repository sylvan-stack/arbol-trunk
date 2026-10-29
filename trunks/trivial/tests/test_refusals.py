# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
"""Refusals of `run`, judged from the command line to the answer (RCT-2, "Accepting a message"): one line
`{"error":{"code","message"}}`, the exit status 1, no folder, no row, and no Driver started. With a home of the test's
own, a stand-in `security`, a stand-in launcher and the fake database: no database server, no Driver and no network."""

import asyncio
import copy
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import fakes
from fakes import FakeDatabase
from stand_ins import security_stand_in, with_capabilities

from arbol_trunk_trivial.cli import start
from arbol_trunk_trivial.database import Acceptance, Accepted, Connect, Connection
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.run import Output
from arbol_trunk_trivial.start import Prepared

CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"
OPEN = "6e2f4a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"
ROUTE = ("--driver", "claude", "--subscription", "anthropic", "--model", "sonnet")

# A launcher that only notes that it was started, and ends at once without an event.
LAUNCHER = """#!/bin/sh
printf '%s\\n' "$*" >> "$STANDIN_LOG/starts"
"""


class StartTest(unittest.TestCase):
    """A home with the Root `rct`, `~/.arbol/database.json`, no Keychain item, the stand-in launcher on the search
    path and the fake database, in which a whole start runs."""

    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(os.path.realpath(folder.name))
        self.root = roots_folder(self.home) / "rct"
        self.exchanges = self.root / "exchanges"
        self.exchanges.mkdir(parents=True)
        self.root_json({"database": "arbol_rct", "rootContract": 1})
        (self.home / ".arbol").mkdir()
        (self.home / ".arbol" / "database.json").write_text(json.dumps({"address": "postgresql://rct@%2Ftmp%2Fx"}))
        self.security = security_stand_in(self.home, status=44)
        self.bin = self.home / "bin"
        self.bin.mkdir()
        (self.bin / "arbol-claude-driver").write_text(with_capabilities(LAUNCHER))
        os.chmod(self.bin / "arbol-claude-driver", 0o755)
        self.work = self.home / "work"
        self.work.mkdir()
        self.database = FakeDatabase()

    def root_json(self, value: Any) -> None:
        (self.root / "root.json").write_text(value if isinstance(value, str) else json.dumps(value))

    def start(self, *args: str, request: dict[str, Any] | None = None, root: str = "rct", command: str = "run",
              started: float | None = None) -> tuple[int, list[str]]:
        """`--root <root> <command> [--request <file>] <args>` from the command line to its end; its exit status and
        the lines it wrote on standard output."""
        lines: list[str] = []
        request_args: tuple[str, ...] = ()
        if request is not None:
            file = self.home / "start.json"
            file.write_text(json.dumps(request))
            request_args = ("--request", str(file))

        def connector(_prepared: Prepared) -> Connect:
            return self.database.connect()

        with mock.patch.dict("os.environ", {"STANDIN_LOG": str(self.home), "ARBOL_TEST_TIME_SCALE": "10"}):
            status = asyncio.run(start(
                ["--root", root, command, *request_args, *args], home=self.home,
                started=time.monotonic() if started is None else started, connector=connector,
                security=str(self.security), started_in=str(self.work), output=Output(lines.append),
                search_path=f"{self.bin}:/usr/bin:/bin"))
        return status, lines

    def tables(self) -> dict[str, Any]:
        db = self.database
        return copy.deepcopy({"chats": db.chats, "exchanges": db.exchanges, "messages": db.messages,
                              "tool_calls": db.tool_calls, "runs": db.runs, "saves": db.saves})

    def refused(self, code: str, *args: str, request: dict[str, Any] | None = None, root: str = "rct",
                command: str = "run", started: float | None = None) -> str:
        """Judges a refusal: one line `{"error":{"code","message"}}` with `code`, the exit status 1, no folder, no
        row, and no Driver started. Gives its message."""
        before = self.tables()
        status, lines = self.start(*args, request=request, root=root, command=command, started=started)
        self.assertEqual(len(lines), 1, lines)
        answer = json.loads(lines[0])
        self.assertEqual(list(answer), ["error"], answer)
        self.assertEqual(sorted(answer["error"]), ["code", "message"], answer)
        self.assertEqual(answer["error"]["code"], code, answer)
        self.assertIsInstance(answer["error"]["message"], str)
        self.assertTrue(answer["error"]["message"])
        self.assertEqual(lines[0], json.dumps(answer, ensure_ascii=False, separators=(",", ":")))
        self.assertEqual(status, 1)
        self.assertEqual(os.listdir(self.exchanges) if self.exchanges.exists() else [], [])
        self.assertEqual(self.tables(), before)
        self.assertFalse((self.home / "starts").exists(), "a Driver was started")
        message: str = answer["error"]["message"]
        return message


class WholeStart(StartTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class InvalidInput(StartTest):
    """Refused from the options and the request file alone, before the Root, the settings or the Keychain is read."""

    def setUp(self) -> None:
        super().setUp()
        self.root_json("{")  # a start that read the Root would be refused with unknown_root instead


class NoDriver(StartTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class TheRootTheKeychainAndTheFolder(StartTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class TheDatabaseAtAcceptance(StartTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class SlowAcceptance(FakeDatabase):
    """Connects at once; its acceptance never answers."""

    def connect(self) -> Connect:
        async def connect() -> Connection:
            self.connections += 1
            return SlowConnection(self)

        return connect


class SlowConnection(fakes.FakeConnection):
    async def accept(self, acceptance: Acceptance) -> Accepted:
        await asyncio.sleep(60)
        raise AssertionError("unreachable")



# Archived complete imports; restore needed names in their original scope, not at this file tail.
