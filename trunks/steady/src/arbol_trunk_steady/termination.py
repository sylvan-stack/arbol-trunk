"""End the Trunk's process group without writing an Exchange end (RCT-2.8)."""

from __future__ import annotations

import os
import signal
import threading
import time
from types import FrameType
from typing import NoReturn

from .clock import scaled, uptime

GRACE_SECONDS = 5.0


def install_handlers() -> None:
    """SIGINT and foreground SIGHUP take the termination path too; detach() later ignores SIGHUP."""
    for number in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(number, _terminated)


def _terminated(number: int, frame: FrameType | None) -> NoReturn:
    end_group()


def end_group() -> NoReturn:
    """Let Drivers stop their vendor groups on SIGTERM, then kill what remains after five awake seconds.

    The Trunk stays alive until SIGKILL, with its loop stopped and further termination signals ignored. Its watch
    uses this same function; neither path gets back to the code that writes the Exchange's end.
    """
    if threading.current_thread() is threading.main_thread():
        for number in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(number, signal.SIG_IGN)
    group = os.getpgrp()
    os.killpg(group, signal.SIGTERM)
    deadline = uptime() + scaled(GRACE_SECONDS)
    while (remaining := deadline - uptime()) > 0:
        time.sleep(remaining)
    os.killpg(group, signal.SIGKILL)
    os._exit(128 + signal.SIGKILL)  # the group includes this process; also never return if killpg is substituted
