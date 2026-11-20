"""Read callback counts from Forester's append-only Ledger during the exclusive chat run."""

import json
import os
import stat
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

HOOKS = frozenset({
    "session-start", "session-end", "pre-tool-use", "post-tool-use",
    "user-prompt-submit", "stop", "post-compact", "other",
})


class ForesterUpdates:
    def __init__(self, home: Path, chat: str) -> None:
        self.root = home / "Artifacts" / "forester"
        self.chat = chat
        self.chat_bytes = chat.encode("ascii")
        self.counts: dict[str, int] = {}
        today = datetime.now(UTC).date()
        self.offsets = {day: self.size(day) for day in (today - timedelta(days=1), today)}

    def path(self, day: date) -> Path:
        return self.root / "ledger" / f"{day:%Y}" / f"{day:%m}" / f"{day}.jsonl"

    def size(self, day: date) -> int:
        try:
            info = self.path(day).lstat()
            return info.st_size if stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() else 0
        except OSError:
            return 0

    def refresh(self) -> dict[str, int] | None:
        before = self.counts.copy()
        self.offsets.setdefault(datetime.now(UTC).date(), 0)
        for day, offset in self.offsets.items():
            try:
                flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
                with os.fdopen(os.open(self.path(day), flags), "rb") as stream:
                    info = os.fstat(stream.fileno())
                    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
                        continue
                    stream.seek(offset)
                    while self.offsets[day] < info.st_size and (line := stream.readline()):
                        if not line.endswith(b"\n"):
                            break
                        self.offsets[day] += len(line)
                        if self.chat_bytes in line:
                            self.take(line)
            except OSError:
                continue
        return self.counts.copy() if self.counts != before else None

    def take(self, line: bytes) -> None:
        try:
            record = json.loads(line)
        except (ValueError, RecursionError):
            return
        if not isinstance(record, dict) or record.get("type") != "hook":
            return
        data = record.get("data")
        if not isinstance(data, dict) or data.get("arbolChat") != self.chat:
            return
        event = data.get("event")
        if isinstance(event, str) and event in HOOKS:
            self.counts[event] = self.counts.get(event, 0) + 1
