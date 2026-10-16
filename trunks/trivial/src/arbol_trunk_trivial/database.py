"""The Root's database (RCT-0, RCT-3): psycopg 3's asynchronous connection, with a limit of 5 seconds to connect and
for each statement, so that no call holds up the Trunk's loop for longer (RCT-2, TRV-D9).

The address of `~/.arbol/database.json` reaches the server; the database that `root.json` names takes the place of any
database the address names. The limit of a call is not divided by ARBOL_TEST_TIME_SCALE (RCT-4).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

import psycopg
from psycopg import errors as sqlstate
from psycopg.conninfo import make_conninfo
from psycopg.types.json import Jsonb

from . import NAME
from .history import HistoryRow

CALL_SECONDS = 5.0


class DatabaseUnavailable(Exception):
    """A call to the database failed or did not end within its limit; the connection is given up."""


class ChatBusy(Exception):
    """The chat has an open Exchange, or another message to it was accepted at the same moment (RCT-2)."""

    def __init__(self, open_exchange: str | None) -> None:
        super().__init__(open_exchange)
        self.open_exchange = open_exchange


@dataclass(frozen=True)
class Acceptance:
    """What the acceptance writes: the chat when it is new, the open Exchange, and the message at position 0."""

    exchange: str
    chat: str
    message: str
    trunk: str
    build: str
    route: dict[str, Any]
    small_call_route: dict[str, Any] | None
    working_folder: str
    accepted_at: datetime


@dataclass(frozen=True)
class Accepted:
    number: int  # the Exchange's place in its chat
    history: list[HistoryRow]  # the rows of the chat's earlier Exchanges, read in the same transaction


class Connection(Protocol):
    """The calls the Trunk makes on its Root's database."""

    async def accept(self, acceptance: Acceptance) -> Accepted: ...

    async def close(self) -> None: ...


Connect = Callable[[], Coroutine[Any, Any, Connection]]


def conninfo(address: str, database: str, password: str | None) -> str:
    extra: dict[str, Any] = {"dbname": database, "connect_timeout": int(CALL_SECONDS), "application_name": NAME,
                             "options": f"-c statement_timeout={int(CALL_SECONDS * 1000)}"}
    if password is not None:
        extra["password"] = password
    return make_conninfo(address, **extra)


async def within_limit[T](call: Awaitable[T]) -> T:
    try:
        return await asyncio.wait_for(call, CALL_SECONDS)
    except TimeoutError:
        raise DatabaseUnavailable(f"The database did not answer within {CALL_SECONDS:g} seconds.") from None
    except psycopg.Error as error:
        raise DatabaseUnavailable(str(error).strip() or type(error).__name__) from error


BUSY = ("exchanges_one_open_per_chat", "exchanges_chat_id_number_key")

HISTORY = """
SELECT e.number, m.position, e.replaced_by IS NOT NULL, m.role, m.text,
       NULL::text, NULL::jsonb, NULL::boolean, NULL::jsonb, NULL::text, NULL::text
  FROM exchanges e JOIN messages m ON m.exchange_id = e.id
 WHERE e.chat_id = %(chat)s AND e.number < %(number)s AND e.replaced_by IS NULL
UNION ALL
SELECT e.number, t.position, e.replaced_by IS NOT NULL, NULL, NULL,
       t.name, t.input, t.ok, t.result, t.error, t.parent_call_id
  FROM exchanges e JOIN tool_calls t ON t.exchange_id = e.id
 WHERE e.chat_id = %(chat)s AND e.number < %(number)s AND e.replaced_by IS NULL AND t.parent_call_id IS NULL
 ORDER BY 1, 2
"""


class PostgresConnection:
    def __init__(self, connection: psycopg.AsyncConnection[Any]) -> None:
        self.connection = connection

    async def accept(self, acceptance: Acceptance) -> Accepted:
        """One transaction: the chat with an insert that does nothing when it is there, the open Exchange with the
        next number in its chat, the message at position 0, and the history of the chat (RCT-2, TRV-D3)."""
        a = acceptance
        try:
            async with self.connection.transaction(), self.connection.cursor() as cursor:
                await within_limit(cursor.execute(
                    "INSERT INTO chats (id, created_at) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (a.chat, a.accepted_at)))
                await within_limit(cursor.execute(
                    "SELECT coalesce(max(number), 0) + 1 FROM exchanges WHERE chat_id = %s", (a.chat,)))
                found = await cursor.fetchone()
                number = int(found[0]) if found else 1
                await within_limit(cursor.execute(
                    "INSERT INTO exchanges (id, chat_id, number, state, trunk, build, route, small_call_route,"
                    " working_folder, accepted_at) VALUES (%s, %s, %s, 'open', %s, %s, %s, %s, %s, %s)",
                    (a.exchange, a.chat, number, a.trunk, a.build, Jsonb(a.route),
                     None if a.small_call_route is None else Jsonb(a.small_call_route), a.working_folder,
                     a.accepted_at)))
                await within_limit(cursor.execute(
                    "INSERT INTO messages (exchange_id, position, role, text) VALUES (%s, 0, 'user', %s)",
                    (a.exchange, a.message)))
                await within_limit(cursor.execute(HISTORY, {"chat": a.chat, "number": number}))
                rows = await cursor.fetchall()
        except DatabaseUnavailable as error:
            if isinstance(error.__cause__, sqlstate.UniqueViolation) and error.__cause__.diag.constraint_name in BUSY:
                raise ChatBusy(await self.open_exchange(a.chat)) from None
            raise
        return Accepted(number, [HistoryRow(*row) for row in rows])

    async def open_exchange(self, chat: str) -> str | None:
        try:
            async with self.connection.cursor() as cursor:
                await within_limit(cursor.execute(
                    "SELECT id::text FROM exchanges WHERE chat_id = %s AND state = 'open'", (chat,)))
                found = await cursor.fetchone()
        except DatabaseUnavailable:
            return None
        return str(found[0]) if found else None

    async def close(self) -> None:
        try:
            await asyncio.wait_for(self.connection.close(), 1.0)
        except (TimeoutError, psycopg.Error, OSError):
            pass


def postgres(info: str) -> Connect:
    """What connects to the Root's database, each time it is called on a new connection."""

    async def connect() -> Connection:
        return PostgresConnection(await within_limit(psycopg.AsyncConnection.connect(info, autocommit=True)))

    return connect
