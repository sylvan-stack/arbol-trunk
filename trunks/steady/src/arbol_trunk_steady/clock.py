"""Times as the Root Contract writes them, and the waits that ARBOL_TEST_TIME_SCALE divides (RCT-1, RCT-4)."""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime


def iso(moment: datetime | None = None) -> str:
    """A time in the form JavaScript's toISOString writes, such as 2026-10-15T09:30:00.412Z."""
    moment = (moment or datetime.now(UTC)).astimezone(UTC)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def time_scale() -> float:
    """ARBOL_TEST_TIME_SCALE, 1 when it is not set or not a positive number."""
    try:
        value = float(os.environ.get("ARBOL_TEST_TIME_SCALE", "1"))
    except ValueError:
        return 1.0
    return value if value > 0 else 1.0


def scaled(seconds: float) -> float:
    """A wait of the contract that ARBOL_TEST_TIME_SCALE divides."""
    return seconds / time_scale()


def uptime() -> float:
    """CLOCK_UPTIME_RAW: it stands still while the Mac sleeps (RCT-1)."""
    return time.clock_gettime(time.CLOCK_UPTIME_RAW)


class Clock:
    """The clock the loop counts the times of a run with (TRV-0, "Stopping the run"): CLOCK_UPTIME_RAW. A unit test
    gives a clock of its own, which it moves."""

    def now(self) -> float:
        return uptime()


UPTIME = Clock()
