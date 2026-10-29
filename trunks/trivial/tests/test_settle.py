# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import asyncio
import json
import os
import tempfile
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path

from fakes import Exchange, FakeDatabase

from arbol_trunk_trivial.cli import start
from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.output import Output
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.settle import Settlement, open_settlement, settle_exchange

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
AT = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)


class SettlementTest(unittest.TestCase):
    def setUp(self) -> None:
        name = tempfile.TemporaryDirectory()
        self.addCleanup(name.cleanup)
        self.home = Path(name.name)
        self.root = roots_folder(self.home) / "rct"
        self.exchanges = self.root / "exchanges"
        self.exchanges.mkdir(parents=True)
        (self.root / "root.json").write_text(json.dumps({"database": "arbol_rct", "rootContract": 1}))
        self.record = {"exchange": X, "process": {"pid": os.getpid(), "startedAt": "2000-01-01T00:00:00Z"},
                       "acceptedAt": AT.isoformat()}
        self.folder = ExchangeFolder.make(self.exchanges, X, self.record)
        self.database = FakeDatabase()
        self.database.exchanges[X] = Exchange(X, "chat", 1, "open", "trivial", "0", {}, None, "/w", AT)

    def open(self) -> Settlement | None:
        return asyncio.run(open_settlement(self.home, "rct", X, connect=self.database.connect()))


class OpeningSettlement(SettlementTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class ReplayingSettlement(SettlementTest):
    def write(self, *lines: object, tail: bytes = b"") -> None:
        data = b"".join(json.dumps(line).encode() + b"\n" for line in lines)
        (self.folder.path / "events.jsonl").write_bytes(data + tail)


class SavingSettlement(SettlementTest):
    def settle(self) -> tuple[int, dict[str, object]]:
        lines: list[str] = []
        status = asyncio.run(start(["--root", "rct", "settle", X], home=self.home, started=time.monotonic(),
                                   output=Output(lines.append), settle_connect=self.database.connect()))
        self.assertEqual(len(lines), 1)
        return status, json.loads(lines[0])


# Archived complete imports; restore needed names in their original scope, not at this file tail.
