__all__ = [
    "AcceptanceHome", "CHAT", "Refusal",
]
# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.

import asyncio
import os
import tempfile
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path

from fakes import FakeDatabase, unit_installation

from arbol_trunk_trivial.accept import Exchange, accept_in_database, accept_message
from arbol_trunk_trivial.admission import Admission
from arbol_trunk_trivial.command import handed, parse
from arbol_trunk_trivial.database import Acceptance, Accepted, Connection
from arbol_trunk_trivial.errors import Refusal
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
        self.installation = unit_installation(self.home)
        self.exchanges = self.installation.exchanges

    def prepared(self, *args: str) -> Prepared:
        return prepare(handed(parse(["run", *args]), started_in=str(self.home)), self.installation)

    def accept(self, database: FakeDatabase, *args: str) -> Exchange:
        with Admission(self.installation.runtime).lease("normal"):
            return asyncio.run(accept_message(self.prepared("--driver", "claude", *args), database.connect(), build="0",
                                              process={"pid": 48213, "startedAt": "2026-10-15T09:30:00.000Z"},
                                              started=time.monotonic()))


class AcceptingAMessage(AcceptanceHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
