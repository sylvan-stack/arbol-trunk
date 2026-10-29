# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import asyncio
from unittest import mock

from fakes import FakeConnection, FakeDatabase
from test_accept import CHAT, AcceptanceHome

from arbol_trunk_trivial.database import Acceptance, Accepted
from arbol_trunk_trivial.errors import Refusal

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
Y = "2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"
Z = "9b3a2c1e-5c6d-4f70-9a1b-2c3d4e5f6a7b"


class ReplacementHome(AcceptanceHome):
    def original(self) -> FakeDatabase:
        database = FakeDatabase()
        first = self.accept(database, "--exchange", X, "--chat", CHAT, "original message")
        asyncio.run(first.connection.close())
        first.folder.discard()
        original = database.exchanges[X]
        original.state, original.ended_at = "completed", original.accepted_at
        database.messages[(X, 2)] = ("assistant", "discard this answer")
        database.tool_calls[(X, 3)] = {"name": "shell", "input": {"command": "old"}, "ok": True}
        database.runs[(X, "run")] = {"usage": {"inputTokens": 41}}
        return database


class ReplacingAMessage(ReplacementHome):
    pass  # Shared fixture base; case bodies live in top/ and mid/.


class ReplacementHistory(ReplacementHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.

# Archived complete imports; restore needed names in their original scope, not at this file tail.
