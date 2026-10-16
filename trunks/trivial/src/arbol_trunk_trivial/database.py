"""The Root's database (RCT-0, RCT-3): psycopg 3's asynchronous connection, with a limit of 5 seconds to connect and
for each statement, so that no call holds up the Trunk's loop for longer (RCT-2, TRV-D9).

The address of `~/.arbol/database.json` reaches the server; the database that `root.json` names takes the place of any
database the address names. The limit of a call is not divided by ARBOL_TEST_TIME_SCALE (RCT-4).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Protocol

import psycopg
from psycopg.conninfo import make_conninfo

from . import NAME

CALL_SECONDS = 5.0


class DatabaseUnavailable(Exception):
    """A call to the database failed or did not end within its limit; the connection is given up."""


class Connection(Protocol):
    """The calls the Trunk makes on its Root's database."""

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


class PostgresConnection:
    def __init__(self, connection: psycopg.AsyncConnection[Any]) -> None:
        self.connection = connection

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
