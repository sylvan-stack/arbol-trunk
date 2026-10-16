"""The Trunk's own process as the record names it: its identifier and the time the system gives as its start, as
`ps -o lstart= -p <pid>` prints it (RCT-1)."""

from __future__ import annotations

import os
import subprocess
from datetime import datetime

from .clock import iso


def started_at(pid: int | None = None) -> str:
    pid = os.getpid() if pid is None else pid
    output = subprocess.run(["/bin/ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True, check=True,
                            env={"LANG": "C", "LC_ALL": "C", "PATH": "/usr/bin:/bin"}, timeout=5).stdout
    return iso(datetime.strptime(" ".join(output.split()), "%a %b %d %H:%M:%S %Y").astimezone())
