"""The one thread that only observes progress and ends a stuck Trunk (RCT-1.4)."""

from __future__ import annotations

import threading
from collections.abc import Callable

from .clock import scaled
from .life import SignsOfLife
from .termination import end_group

LOOK_SECONDS = 1.0
STUCK_SECONDS = 60.0


class Watch:
    def __init__(self, life: SignsOfLife, end: Callable[[], None] | None = None) -> None:
        self.life = life
        self.end = end if end is not None else end_group
        self.done = threading.Event()
        self.thread: threading.Thread | None = None

    def look(self) -> bool:
        """Only awake time since the work's last raise counts; the watch never raises or writes anything."""
        if self.life.clock.now() - self.life.last_raised < scaled(STUCK_SECONDS):
            return False
        self.end()
        return True

    def start(self) -> None:
        self.thread = threading.Thread(target=self._run, name="trunk-watch", daemon=True)
        self.thread.start()

    def _run(self) -> None:
        while not self.done.wait(scaled(LOOK_SECONDS)):
            if self.look():
                return

    def close(self) -> None:
        self.done.set()
        if self.thread is not None:
            self.thread.join()
            self.thread = None
