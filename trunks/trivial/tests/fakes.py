"""A fake of the Root's database for the unit tests: no server, no network."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from arbol_trunk_trivial.database import Acceptance, Accepted, ChatBusy, Connect, Connection, DatabaseUnavailable
from arbol_trunk_trivial.history import HistoryRow
from arbol_trunk_trivial.rows import MessageRow, Row, RunRow, ToolCallRow


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
    fail_save: int = 0  # the next n saves fail
    fail_end: int = 0  # the next n end transactions fail
    ends: int = 0
    delay: float = 0.0  # each call waits this long first
    saves: list[Row] = field(default_factory=list)  # every row saved, in order, a row saved twice twice

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

    async def save(self, row: Row) -> None:
        await self._call()
        db = self.database
        if db.fail_save:
            db.fail_save -= 1
            raise DatabaseUnavailable("The fake database refused the call.")
        db.saves.append(row)
        if isinstance(row, MessageRow):
            db.messages.setdefault((row.exchange, row.position), ("assistant", row.text))
        elif isinstance(row, ToolCallRow):
            db.tool_calls.setdefault((row.exchange, row.position), {
                "name": row.name, "input": row.input, "ok": row.ok, "result": row.result, "error": row.error,
                "parent_call_id": row.parent_call_id, "interrupted": row.interrupted, "run_id": row.run_id})
        elif isinstance(row, RunRow):
            db.runs.setdefault((row.exchange, row.run_id), {
                "kind": row.kind, "outcome": row.outcome, "usage": row.usage, "error": row.error,
                "started": row.started, "ended_at": row.ended_at})

    async def end(self, exchange: str, rows: Sequence[Row], state: str, ended_at: datetime,
                  error: dict[str, Any] | None) -> None:
        await self._call()
        db = self.database
        if db.fail_end:
            db.fail_end -= 1
            raise DatabaseUnavailable("The fake database refused the end.")
        db.ends += 1
        saves, failing = db.saves, db.fail_save
        db.fail_save = 0
        for row in rows:
            await self.save(row)
        db.fail_save, db.saves = failing, saves
        found = db.exchanges.get(exchange)
        if found is not None and found.state == "open":
            found.state, found.ended_at, found.error = state, ended_at, error
