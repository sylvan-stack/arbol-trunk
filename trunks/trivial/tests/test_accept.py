# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import asyncio
import json
import os
import tempfile
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path

from fakes import FakeDatabase
from stand_ins import security_stand_in

from arbol_trunk_trivial.accept import Exchange, accept_in_database, accept_message
from arbol_trunk_trivial.command import handed, parse
from arbol_trunk_trivial.database import Acceptance, Accepted, Connection
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.start import Prepared, prepare

CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"
ROUTE = {"driver": "claude", "subscription": "anthropic", "model": "sonnet", "effort": "high"}
SMALL = {"driver": "claude", "subscription": "anthropic", "model": "haiku"}


def acceptance(exchange: str, message: str = "What does build.sh do?", chat: str = CHAT) -> Acceptance:
    return Acceptance(exchange, chat, message, "trivial", "0", ROUTE, SMALL, "/Users/sam/repos/shop",
                      datetime(2026, 10, 15, 9, 30, tzinfo=UTC))


def accept(database: FakeDatabase, value: Acceptance, seconds: float = 10.0) -> tuple[Connection, Accepted]:
    return asyncio.run(accept_in_database(database.connect(), value, time.monotonic() + seconds))


class Acceptances(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class AcceptanceHome(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(os.path.realpath(folder.name))
        root = roots_folder(self.home) / "rct"
        self.exchanges = root / "exchanges"
        self.exchanges.mkdir(parents=True)
        (root / "root.json").write_text(json.dumps({"database": "arbol_rct", "rootContract": 1}))
        (self.home / ".arbol").mkdir()
        (self.home / ".arbol" / "database.json").write_text(json.dumps({"address": "postgresql://rct@%2Ftmp%2Fx"}))
        self.security = str(security_stand_in(self.home, status=44))

    def prepared(self, *args: str) -> Prepared:
        return prepare(handed(parse(["--root", "rct", "run", *args]), started_in=str(self.home)), self.home,
                       self.security)

    def accept(self, database: FakeDatabase, *args: str) -> Exchange:
        return asyncio.run(accept_message(self.prepared("--driver", "claude", *args), database.connect(), build="0",
                                          process={"pid": 48213, "startedAt": "2026-10-15T09:30:00.000Z"},
                                          started=time.monotonic()))


class AcceptingAMessage(AcceptanceHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.



# Archived complete imports; restore needed names in their original scope, not at this file tail.
