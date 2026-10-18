"""The end of an Exchange (RCT-2, "The end").

Every accepted Exchange ends exactly once, on every path, and the Trunk ends it by itself: first the end line in
`events.jsonl` and the same `end` in the record; then the rows not yet saved and the final state in one transaction that
changes the Exchange only while it is open; then the folder is removed. With one run the state is the run's outcome: a
failed run keeps the Driver's whole error object, and a run whose Driver could not be started, or ended without a
`finished` event, fails with `driver_failed`.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .clock import iso, scaled, uptime
from .database import DatabaseUnavailable
from .events import EventsFile
from .folder import ExchangeFolder
from .rows import Row
from .saver import RETRY_SECONDS, Saver

EXIT_STATUS = {"completed": 0, "failed": 1, "cancelled": 2}
NO_FINISHED = "The Driver's process ended without a finished event."
END_TRIES_SECONDS = 60.0  # divided by ARBOL_TEST_TIME_SCALE (RCT-4)


@dataclass(frozen=True)
class End:
    state: str  # completed, failed or cancelled
    at: datetime
    error: dict[str, Any] | None = None

    def value(self) -> dict[str, Any]:
        end: dict[str, Any] = {"state": self.state, "at": iso(self.at)}
        if self.error is not None:
            end["error"] = self.error
        return end

    @property
    def exit_status(self) -> int:
        return EXIT_STATUS[self.state]


def failed(code: str, message: str) -> End:
    return End("failed", datetime.now(UTC), {"code": code, "message": message})


def cancelled() -> End:
    return End("cancelled", datetime.now(UTC))


def end_of_run(finished: dict[str, Any] | None) -> End:
    """The end that the run's `finished` event gives, or `driver_failed` without one."""
    if finished is None:
        return failed("driver_failed", NO_FINISHED)
    outcome = finished.get("outcome")
    if outcome in ("completed", "cancelled"):
        return End(str(outcome), datetime.now(UTC))
    error = finished.get("error")
    if not isinstance(error, dict):
        error = {"code": "driver_failed", "message": "The Driver's run failed without an error object."}
    return End("failed", datetime.now(UTC), error)


def write_end(events: EventsFile, folder: ExchangeFolder, end: End) -> None:
    """The end line as the last line of `events.jsonl`, and the same `end` in the record."""
    events.append_end(end.value())
    folder.update(end=end.value())


async def save_end(saver: Saver, exchange: str, rows_at_end: Sequence[Row], end: End) -> bool:
    """The rows not yet saved and the final state in one transaction, tried every 5 seconds for 60 seconds; True once
    the database holds the end. The saving task is stopped first; its connection is used when it has one."""
    await saver.stop()
    rows = [*saver.unsaved, *rows_at_end]
    connection, saver.connection = saver.connection, None
    deadline = uptime() + scaled(END_TRIES_SECONDS)
    while True:
        try:
            if connection is None:
                connection = await saver.connect()
            await connection.end(exchange, rows, end.state, end.at, end.error)
            await connection.close()
            return True
        except DatabaseUnavailable:
            if connection is not None:
                await connection.close()
                connection = None
            if uptime() + scaled(RETRY_SECONDS) > deadline:
                return False
            await asyncio.sleep(scaled(RETRY_SECONDS))


async def finish(saver: Saver, folder: ExchangeFolder, rows_at_end: Sequence[Row], end: End) -> bool:
    """Saves the end and then removes the folder; when the database does not take it within its tries, the folder
    stays, with `end` in its record, for settling (RCT-2)."""
    if not await save_end(saver, folder.exchange, rows_at_end, end):
        return False
    folder.remove()
    return True
