"""The Trunk's own process as the record names it: its identifier and the time the system gives as its start, as
`ps -o lstart= -p <pid>` prints it (RCT-1)."""

from __future__ import annotations

import os
import subprocess
from datetime import datetime
from typing import Any

from .clock import iso
from .errors import Refusal


def started_at(pid: int | None = None) -> str:
    pid = os.getpid() if pid is None else pid
    output = subprocess.run(["/bin/ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True, check=True,
                            env={"LANG": "C", "LC_ALL": "C", "PATH": "/usr/bin:/bin"}, timeout=5).stdout
    return iso(datetime.strptime(" ".join(output.split()), "%a %b %d %H:%M:%S %Y").astimezone())


def process_alive(process: Any) -> bool:
    """The PID must still have the recorded start time, give or take two seconds (RCT-1)."""
    if not isinstance(process, dict) or not isinstance(process.get("pid"), int) or isinstance(process["pid"], bool):
        raise Refusal("trunk_failed", "The Exchange record names no process.")
    try:
        recorded = datetime.fromisoformat(process["startedAt"])
        if recorded.tzinfo is None or process["pid"] <= 0:
            raise ValueError("A process needs a positive PID and an absolute start time.")
    except (KeyError, TypeError, ValueError):
        raise Refusal("trunk_failed", "The Exchange record names no readable process start time.") from None
    try:
        actual = datetime.fromisoformat(started_at(process["pid"]))
    except subprocess.CalledProcessError:
        return False
    except (OSError, ValueError, subprocess.TimeoutExpired):
        raise Refusal("trunk_failed", "The recorded process could not be checked safely.") from None
    return abs((actual - recorded).total_seconds()) <= 2
