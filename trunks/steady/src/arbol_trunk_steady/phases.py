"""Prepare accepted Exchange data and hand it to the next phase."""

import asyncio
import json
import subprocess
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

from .end import End


@dataclass
class ExchangeData:
    cue_context: str | None


def prepare_cue_context(home: Path, folder: Path, message: str) -> str | None:
    """Use Forester's non-hook preparation. None leaves delivery to the usual path."""
    try:
        prepared = subprocess.run(
            [str(home / ".local/bin/forester"), "cues", "prepare", "--overflow-file", str(folder / "cues.md")],
            input=message.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=5, check=False,
        )
        if prepared.returncode != 0 or len(prepared.stdout) > 256 * 1024:
            return None
        value = json.loads(prepared.stdout)
        context = value.get("context") if isinstance(value, dict) else None
        if not isinstance(context, str) or len(context) > 8000 or "\0" in context:
            return None
        context.encode("utf-8")
        return context
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None


async def intake(home: Path, folder: Path, message: str, execute: Callable[[ExchangeData], Awaitable[End]]) -> End:
    context = await asyncio.to_thread(prepare_cue_context, home, folder, message)
    return await planning(ExchangeData(cue_context=context), execute)


async def planning(data: ExchangeData, execute: Callable[[ExchangeData], Awaitable[End]]) -> End:
    """Continue to Execution with the public Exchange data."""
    return await execute(data)


def finalization(outcome: End) -> End:
    """Pass the outcome to the shared Exchange end handling."""
    return outcome
