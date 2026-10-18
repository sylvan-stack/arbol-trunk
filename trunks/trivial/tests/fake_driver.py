"""A Driver run on a clock the test moves, for the unit tests of the loop: no process, no Driver and no waiting."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from arbol_trunk_trivial.clock import Clock
from arbol_trunk_trivial.driver import Line

KILLED = -9


class MovedClock(Clock):
    """A clock that stands still until the test, or a fake Driver's wait, moves it."""

    def __init__(self, start: float = 1000.0) -> None:
        self.start = start
        self.t = start

    def now(self) -> float:
        return self.t

    def since_start(self) -> float:
        return round(self.t - self.start, 6)


class ScriptedDriver:
    """A Driver run that plays a timeline on a MovedClock: events, the end of its output and its exit, each at a time
    in seconds from the clock's start. A read waits by moving the clock, to the next item of the timeline or by the
    whole wait. `on_control` is called with each line written to the control input, `holds_output` keeps the output
    open after the process has ended, as a child of the Driver would."""

    def __init__(self, clock: MovedClock, *, holds_output: bool = False) -> None:
        self.clock = clock
        self.holds_output = holds_output
        self.timeline: list[tuple[float, str, Any]] = []
        self.returncode: int | None = None
        self.output_ended = False
        self.control: list[tuple[float, str]] = []  # each line written to the control input, at its time
        self.killed_at: float | None = None
        self.waits: list[float] = []  # every wait the loop asked for
        self.on_control: Callable[[str], None] | None = None

    def at(self, seconds: float, kind: str, value: Any = None) -> None:
        """Adds an item at `seconds` from the clock's start: "event" (a dict), "end_output" or "exit" (a status)."""
        self.timeline.append((self.clock.start + seconds, kind, value))
        self.timeline.sort(key=lambda item: item[0])

    def after(self, seconds: float, kind: str, value: Any = None) -> None:
        """Adds an item at `seconds` from now."""
        self.at(self.clock.since_start() + seconds, kind, value)

    async def read(self, seconds: float) -> list[Line]:
        self.waits.append(seconds)
        until = self.clock.t + seconds
        if not self.timeline or self.timeline[0][0] > until:
            self.clock.t = until
            return []
        moment = self.timeline[0][0]
        self.clock.t = max(self.clock.t, moment)
        lines: list[Line] = []
        while self.timeline and self.timeline[0][0] <= moment:
            _at, kind, value = self.timeline.pop(0)
            if kind == "event" and not self.output_ended:
                lines.append(Line(json.dumps(value), value))
            elif kind == "end_output":
                self.output_ended = True
            elif kind == "exit" and self.returncode is None:
                self.returncode = value
                if not self.holds_output:
                    self.output_ended = True
        return lines

    def write_control(self, line: str) -> None:
        self.control.append((self.clock.since_start(), line))
        if self.on_control is not None:
            self.on_control(line)

    def kill(self) -> None:
        if self.returncode is None:
            self.killed_at = self.clock.since_start()
            self.timeline = [item for item in self.timeline if item[1] != "exit"]
            self.after(0, "exit", KILLED)


def event(seq: int, kind: str, **fields: Any) -> dict[str, Any]:
    return {"runId": "x.1", "seq": seq, "type": kind, **fields}


def finished(seq: int, outcome: str = "completed", **fields: Any) -> dict[str, Any]:
    return event(seq, "finished", outcome=outcome, producedOutput=True, unfinishedCalls=[], **fields)
