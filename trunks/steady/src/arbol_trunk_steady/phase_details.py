"""Private phase data and the ordered journal of an accepted Steady Exchange."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from .clock import iso
from .folder import FILE_MODE

JOURNAL = "phase-details.jsonl"
type PhaseName = Literal["intake", "planning", "execution", "finalization"]


@dataclass
class ExchangeData:
    cue_context: str | None = None
    system_prompt: str | None = None


@dataclass
class PhaseData:
    started_at: str
    finished_at: str | None = None
    commands: list[dict[str, Any]] = field(default_factory=list)
    values: dict[str, Any] = field(default_factory=dict)


class PhaseDetails:
    def __init__(self, folder: Path) -> None:
        self.public = ExchangeData()
        self.private: dict[PhaseName, PhaseData] = {}
        self.current: PhaseName | None = None
        self.path = folder / JOURNAL
        self.position = 0
        self.journal_available = True

    def enter(self, phase: PhaseName) -> None:
        self.finish()
        self.current = phase
        data = self.private[phase] = PhaseData(iso())
        self.record(startedAt=data.started_at)

    def finish(self) -> None:
        if self.current is not None:
            data = self.private[self.current]
            data.finished_at = iso()
            self.record(finishedAt=data.finished_at)
            self.current = None

    def record(self, **values: Any) -> None:
        if self.current is None:
            return
        self.position += 1
        entry = json.dumps({"n": self.position, "phase": self.current, **values}, separators=(",", ":"))
        if self.journal_available:
            try:
                flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW
                with os.fdopen(os.open(self.path, flags, FILE_MODE), "ab") as stream:
                    stream.write((entry + "\n").encode("ascii"))
            except OSError:
                self.journal_available = False
