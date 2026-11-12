__all__ = [
    "MessageRow", "Output", "Refusal", "RunRow", "ToolCallRow", "X", "asyncio", "copy", "json", "mock", "parse",
    "replay", "root_lock", "settle_exchange", "started_at",
]
# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import asyncio
import copy
import json
import os
import tempfile
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

from fakes import Exchange, FakeDatabase, unit_installation

from arbol_trunk_trivial.admission import GENERATION_ENV
from arbol_trunk_trivial.claim import exchange_lock as root_lock
from arbol_trunk_trivial.command import parse
from arbol_trunk_trivial.errors import Refusal
from arbol_trunk_trivial.folder import EXCHANGE_FORMAT, ExchangeFolder
from arbol_trunk_trivial.output import Output
from arbol_trunk_trivial.process import started_at
from arbol_trunk_trivial.rows import MessageRow, RunRow, ToolCallRow
from arbol_trunk_trivial.settle import Settlement, open_settlement, replay, settle_exchange

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"
AT = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)


class SettlementTest(unittest.TestCase):
    def setUp(self) -> None:
        name = tempfile.TemporaryDirectory()
        self.addCleanup(name.cleanup)
        self.home = Path(name.name).resolve()
        self.installation = unit_installation(self.home)
        self.exchanges = self.installation.exchanges
        self.record = {"exchangeFormat": EXCHANGE_FORMAT, "exchange": X, "chat": CHAT, "trunk": "trivial", "build": "0",
                       "process": {"pid": os.getpid(), "startedAt": "2000-01-01T00:00:00Z"}, "acceptedAt": AT.isoformat()}
        self.folder = ExchangeFolder.make(self.exchanges, X, self.record)
        self.database = FakeDatabase()
        self.database.exchanges[X] = Exchange(X, CHAT, 1, "open", "trivial", "0", {}, None, "/w", AT)

    def open(self) -> Settlement | None:
        return asyncio.run(open_settlement(self.installation, X, "0", connect=self.database.connect(),
                                           deadline=time.monotonic() + 10))

    async def settle_once(self, output: Output) -> int:
        return await settle_exchange(self.installation, X, output=output, connect=self.database.connect(),
                                     build="0", compatibility={1: 1})

    def admit_dispatch(self) -> None:
        environment = mock.patch.dict(os.environ, {GENERATION_ENV: "a" * 32})
        environment.start()
        self.addCleanup(environment.stop)


class OpeningSettlement(SettlementTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class ReplayingSettlement(SettlementTest):
    def write(self, *lines: object, tail: bytes = b"") -> None:
        data = b"".join(json.dumps(line).encode() + b"\n" for line in lines)
        (self.folder.path / "events.jsonl").write_bytes(data + tail)


class SavingSettlement(SettlementTest):
    def settle(self) -> tuple[int, dict[str, object]]:
        lines: list[str] = []
        self.admit_dispatch()
        status = asyncio.run(self.settle_once(Output(lines.append)))
        self.assertEqual(len(lines), 1)
        return status, json.loads(lines[0])


# Archived complete imports; restore needed names in their original scope, not at this file tail.
