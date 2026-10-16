"""A fake of the Root's database for the unit tests: no server, no network."""

from __future__ import annotations

import asyncio

from arbol_trunk_trivial.database import Connect, Connection, DatabaseUnavailable


class FakeDatabase:
    """The chat tables in memory, and knobs that make a call slow or fail."""

    def __init__(self) -> None:
        self.connections = 0
        self.closed = 0
        self.fail_connect = 0  # the next n connects fail
        self.delay = 0.0  # each call waits this long first

    def connect(self) -> Connect:
        async def connect() -> Connection:
            self.connections += 1
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
