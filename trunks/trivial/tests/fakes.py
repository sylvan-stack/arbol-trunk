"""A fake of the Root's database for the unit tests: no server, no network."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from arbol_trunk_trivial.database import Acceptance, Accepted, ChatBusy, Connect, Connection, DatabaseUnavailable
from arbol_trunk_trivial.history import HistoryRow


@dataclass
class Exchange:
    id: str
    chat: str
    number: int
    state: str
    trunk: str
    build: str
    route: dict[str, Any]
    small_call_route: dict[str, Any] | None
    working_folder: str
    accepted_at: Any
    ended_at: Any = None
    error: Any = None
    replaced_by: str | None = None


@dataclass
class FakeDatabase:
    """The chat tables in memory, and knobs that make a call slow or fail."""

    chats: dict[str, Any] = field(default_factory=dict)
    exchanges: dict[str, Exchange] = field(default_factory=dict)
    messages: dict[tuple[str, int], tuple[str, str]] = field(default_factory=dict)
    tool_calls: dict[tuple[str, int], dict[str, Any]] = field(default_factory=dict)
    runs: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)
    connections: int = 0
    closed: int = 0
    fail_connect: int = 0  # the next n connects fail
    delay: float = 0.0  # each call waits this long first

    def connect(self) -> Connect:
        async def connect() -> Connection:
            self.connections += 1
            if self.delay:
                await asyncio.sleep(self.delay)
            if self.fail_connect:
                self.fail_connect -= 1
                raise DatabaseUnavailable("The fake database is away.")
            return FakeConnection(self)

        return connect


class FakeConnection:
    def __init__(self, database: FakeDatabase) -> None:
        self.database = database

    async def close(self) -> None:
        self.database.closed += 1

    async def _call(self) -> None:
        if self.database.delay:
            await asyncio.sleep(self.database.delay)

    async def accept(self, acceptance: Acceptance) -> Accepted:
        await self._call()
        db, a = self.database, acceptance
        numbers = [e.number for e in db.exchanges.values() if e.chat == a.chat]
        if any(e.chat == a.chat and e.state == "open" for e in db.exchanges.values()):
            raise ChatBusy(next(e.id for e in db.exchanges.values() if e.chat == a.chat and e.state == "open"))
        db.chats.setdefault(a.chat, a.accepted_at)
        number = max(numbers, default=0) + 1
        db.exchanges[a.exchange] = Exchange(a.exchange, a.chat, number, "open", a.trunk, a.build, a.route,
                                            a.small_call_route, a.working_folder, a.accepted_at)
        db.messages[(a.exchange, 0)] = ("user", a.message)
        rows: list[HistoryRow] = []
        for exchange in db.exchanges.values():
            if exchange.chat != a.chat or exchange.number >= number or exchange.replaced_by is not None:
                continue
            for (exchange_id, position), (role, text) in db.messages.items():
                if exchange_id == exchange.id:
                    rows.append(HistoryRow(exchange.number, position, False, role, text))
            for (exchange_id, position), call in db.tool_calls.items():
                if exchange_id == exchange.id and call.get("parent_call_id") is None:
                    rows.append(HistoryRow(exchange.number, position, False, name=call["name"],
                                           input=call["input"], ok=call["ok"], result=call.get("result"),
                                           error=call.get("error")))
        return Accepted(number, sorted(rows, key=lambda row: (row.number, row.position)))
