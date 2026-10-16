"""The task beside the loop that saves the rows (TRV-0, "One loop and one watch"; TRV-D9; RCT-2).

The loop hands it the rows as their lines reach `events.jsonl` and never waits for it. It saves them one at a time and
in order, each call within 5 seconds. A call that fails or passes its limit is given up with its connection, and the
row waits for the next try, 5 seconds later (divided by ARBOL_TEST_TIME_SCALE), on a new connection.
"""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Sequence

from .clock import scaled
from .database import Connect, Connection, DatabaseUnavailable
from .rows import Row

RETRY_SECONDS = 5.0


class Saver:
    def __init__(self, connect: Connect, connection: Connection | None = None) -> None:
        self.connect = connect
        self.connection = connection
        self.rows: list[Row] = []
        self.saved = 0  # the rows before this index are in the database
        self.failures = 0
        self._wake = asyncio.Event()
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._run())

    def add(self, rows: Sequence[Row]) -> None:
        if rows:
            self.rows.extend(rows)
            self._wake.set()

    @property
    def unsaved(self) -> list[Row]:
        return self.rows[self.saved:]

    async def _run(self) -> None:
        while True:
            if self.saved >= len(self.rows):
                self._wake.clear()
                await self._wake.wait()
                continue
            try:
                if self.connection is None:
                    self.connection = await self.connect()
                await self.connection.save(self.rows[self.saved])
                self.saved += 1
            except DatabaseUnavailable:
                self.failures += 1
                await self.give_up_connection()
                await asyncio.sleep(scaled(RETRY_SECONDS))

    async def give_up_connection(self) -> None:
        connection, self.connection = self.connection, None
        if connection is not None:
            await connection.close()

    async def stop(self) -> None:
        """Stops the task where it is; a row it was saving counts as not saved, and is saved again at the end with an
        insert that does nothing when it is there."""
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None
