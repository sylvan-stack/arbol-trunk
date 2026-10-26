"""Signs of life raised by the work loop, never by a timer (RCT-1.3, TRV-D9)."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any

from .clock import UPTIME, Clock, iso, scaled
from .folder import ExchangeFolder

POLL_SECONDS = 1.0


def waiting_for(*, answer: bool = False, tool: bool = False, driver: bool = False, small_call: bool = False) -> str:
    """The first true wait in the contract's order; the remaining Trunk work serves the database."""
    for active, name in ((answer, "answer"), (tool, "tool"), (driver, "driver"), (small_call, "small-call")):
        if active:
            return name
    return "database"


class SignsOfLife:
    def __init__(self, folder: ExchangeFolder | None = None, clock: Clock = UPTIME) -> None:
        self.folder = folder
        self.clock = clock
        self.last_raised = clock.now()
        self.heartbeat = 0
        self.waiting_for = "database"
        self.since = iso()
        self.questions: set[tuple[str, str]] = set()
        self.tools: set[tuple[str, str]] = set()
        if folder is not None:
            self.bind(folder)

    def bind(self, folder: ExchangeFolder) -> None:
        self.folder = folder
        signs = folder.record["signsOfLife"]
        self.heartbeat = signs["heartbeat"]
        self.waiting_for = signs["waitingFor"]
        self.since = signs["since"]

    def observe(self, event: dict[str, Any]) -> None:
        run = str(event.get("runId", ""))
        kind = event.get("type")
        if kind == "tool_started":
            self.tools.add((run, str(event["callId"])))
        elif kind == "tool_finished":
            self.tools.discard((run, str(event["callId"])))
        elif kind == "ask_opened":
            self.questions.add((run, str(event["askId"])))
        elif kind == "ask_closed":
            self.questions.discard((run, str(event["askId"])))
        elif kind == "finished":
            self.questions = {key for key in self.questions if key[0] != run}
            self.tools = {key for key in self.tools if key[0] != run}

    def waiting(self, *, driver: bool = False, small_call: bool = False) -> str:
        return waiting_for(answer=bool(self.questions), tool=bool(self.tools), driver=driver, small_call=small_call)

    def beat(self, waiting: str | None = None) -> None:
        """One completed round of work: replace the whole record, then publish the awake-clock time to the watch."""
        if waiting is not None and waiting != self.waiting_for:
            if waiting not in ("answer", "tool", "driver", "small-call", "database"):
                raise ValueError("An unknown wait cannot be a sign of life.")
            self.waiting_for, self.since = waiting, iso()
        heartbeat = self.heartbeat + 1
        if self.folder is not None:
            self.folder.update(signsOfLife={"heartbeat": heartbeat, "waitingFor": self.waiting_for, "since": self.since})
        self.heartbeat = heartbeat
        self.last_raised = self.clock.now()

    async def wait[T](self, work: Coroutine[Any, Any, T], waiting: str) -> T:
        """The calling work loop polls a bounded startup/save operation; no independent timer raises a heartbeat."""
        task = asyncio.create_task(work)
        try:
            while not task.done():
                self.beat(waiting)
                await asyncio.wait({task}, timeout=scaled(POLL_SECONDS))
            return task.result()
        finally:
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
