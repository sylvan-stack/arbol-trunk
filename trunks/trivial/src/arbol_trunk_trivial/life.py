"""Signs of life raised by the work loop, never by a timer (RCT-1.3, TRV-D9)."""

from __future__ import annotations

from .clock import UPTIME, Clock, iso
from .folder import ExchangeFolder


class SignsOfLife:
    def __init__(self, folder: ExchangeFolder | None = None, clock: Clock = UPTIME) -> None:
        self.folder = folder
        self.clock = clock
        self.last_raised = clock.now()
        self.heartbeat = 0
        self.waiting_for = "database"
        self.since = iso()
        if folder is not None:
            self.bind(folder)

    def bind(self, folder: ExchangeFolder) -> None:
        self.folder = folder
        signs = folder.record["signsOfLife"]
        self.heartbeat = signs["heartbeat"]
        self.waiting_for = signs["waitingFor"]
        self.since = signs["since"]

    def beat(self) -> None:
        """One completed round of work: replace the whole record, then publish the awake-clock time to the watch."""
        heartbeat = self.heartbeat + 1
        if self.folder is not None:
            self.folder.update(signsOfLife={"heartbeat": heartbeat, "waitingFor": self.waiting_for, "since": self.since})
        self.heartbeat = heartbeat
        self.last_raised = self.clock.now()
