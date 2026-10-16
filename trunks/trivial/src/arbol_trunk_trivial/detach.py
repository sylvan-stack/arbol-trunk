"""The background and the process group (RCT-2, "In the background, or in the foreground", "One process group").

A Trunk leads a process group of its own, whose identifier is its process identifier, and every process it starts for
the Exchange stays in it. With `--detach`, after the acceptance line, it points its standard input, output and error at
`/dev/null` and ignores SIGHUP, and goes on alone.
"""

from __future__ import annotations

import os
import signal
import sys


def lead_process_group() -> None:
    """A Trunk that leads its group when it starts stays in it; one that does not makes itself the leader of a new
    one."""
    if os.getpgrp() != os.getpid():
        os.setpgid(0, 0)


def detach() -> None:
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.flush()
        except (OSError, ValueError):
            pass
    null = os.open(os.devnull, os.O_RDWR)
    try:
        for descriptor in (0, 1, 2):
            os.dup2(null, descriptor)
    finally:
        os.close(null)
