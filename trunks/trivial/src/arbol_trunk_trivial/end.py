"""The end of an Exchange (RCT-2, "The end").

Every accepted Exchange ends exactly once, on every path, and the Trunk ends it by itself: first the end line in
`events.jsonl` and the same `end` in the record; then the rows not yet saved and the final state in one transaction that
changes the Exchange only while it is open; then the folder is removed. With one run the state is the run's outcome: a
failed run keeps the Driver's whole error object, and a run whose Driver could not be started, or ended without a
`finished` event, fails with `driver_failed`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .clock import iso
from .events import EventsFile
from .folder import ExchangeFolder

EXIT_STATUS = {"completed": 0, "failed": 1, "cancelled": 2}
NO_FINISHED = "The Driver's process ended without a finished event."


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
