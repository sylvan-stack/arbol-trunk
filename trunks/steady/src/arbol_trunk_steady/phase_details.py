"""Private phase data and the ordered journal of an accepted Steady Exchange."""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from .clock import iso
from .folder import FILE_MODE
from .rows import PhaseDetailRow

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
    def __init__(self, folder: Path, exchange: str, save: Callable[[PhaseDetailRow], None]) -> None:
        self.public = ExchangeData()
        self.private: dict[PhaseName, PhaseData] = {}
        self.current: PhaseName | None = None
        self.path = folder / JOURNAL
        self.position = 0
        self.journal_available = True
        self.exchange = exchange
        self.save = save

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

    def intake_output(self, data: ExchangeData) -> None:
        self.private["intake"].values["systemPrompt"] = data.system_prompt
        self.public.cue_context = data.cue_context
        self.public.system_prompt = data.system_prompt
        self.record(privatePhase={"systemPrompt": data.system_prompt},
                    publicExchange={"cueContext": data.cue_context, "systemPrompt": data.system_prompt})

    def subprocess(self, argv: list[str], cwd: str, *, standard_input: Any = None,
                   parameters: dict[str, Any] | None = None) -> None:
        entry: dict[str, Any] = {
            "kind": "provider" if parameters is not None else "subprocess",
            "command": argv[0], "arguments": argv[1:], "workingDirectory": cwd,
        }
        if standard_input is not None:
            entry["input"] = standard_input
        if parameters is not None:
            entry["parameters"] = parameters
        self.add_command(entry)

    def add_command(self, entry: dict[str, Any]) -> None:
        if self.current is not None:
            self.private[self.current].commands.append(entry)
            self.record(command=entry)

    def tool_started(self, event: dict[str, Any]) -> None:
        name = event.get("name")
        if isinstance(name, str):
            self.add_command({
                "kind": "tool", "command": name, "parameters": event.get("input"),
                **{key: event[key] for key in ("runId", "callId", "parentCallId") if key in event},
            })

    def record(self, **values: Any) -> None:
        if self.current is None:
            return
        try:
            entry = json.dumps({"n": self.position + 1, "phase": self.current, **values},
                               separators=(",", ":"), allow_nan=False)
        except (ValueError, RecursionError):
            return
        self.position += 1
        if self.journal_available:
            try:
                flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW
                with os.fdopen(os.open(self.path, flags, FILE_MODE), "ab") as stream:
                    stream.write((entry + "\n").encode("ascii"))
            except OSError:
                self.journal_available = False
        self.save(PhaseDetailRow(self.exchange, self.position, entry))


def replay_phase_details(folder: Path, exchange: str) -> list[PhaseDetailRow]:
    """Recover complete, ordered details without making the journal required for settlement."""
    rows: list[PhaseDetailRow] = []
    try:
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        with os.fdopen(os.open(folder / JOURNAL, flags), "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
                return rows
            for raw in stream:
                if not raw.endswith(b"\n"):
                    break
                try:
                    entry = raw[:-1].decode("ascii")
                    value = json.loads(entry)
                except (ValueError, RecursionError):
                    continue
                position = value.get("n") if isinstance(value, dict) else None
                if type(position) is int and 0 < position <= 2147483647 and (
                    not rows or position > rows[-1].position
                ):
                    rows.append(PhaseDetailRow(exchange, position, entry))
    except OSError:
        pass
    return rows
