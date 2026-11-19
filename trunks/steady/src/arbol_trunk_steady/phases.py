"""Prepare accepted Exchange data and hand it to the next phase."""

import asyncio
import json
import subprocess
from collections.abc import Awaitable, Callable
from pathlib import Path

from .end import End
from .phase_details import ExchangeData, PhaseDetails


def prepare_cues(home: Path, folder: Path, message: str, earlier_messages: list[str]) -> ExchangeData:
    """Use Forester's non-hook preparation, falling back to its plain-text interface on older Builds."""
    command = [str(home / ".local/bin/forester"), "cues", "prepare", "--overflow-file", str(folder / "cues.md")]

    def prepare(arguments: list[str], payload: bytes) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(arguments, input=payload, capture_output=True, timeout=5, check=False)

    try:
        payload = json.dumps({"message": message, "earlierMessages": earlier_messages}).encode("utf-8")
        prepared = prepare([*command, "--exchange-json"], payload)
        if prepared.returncode == 2 and b"unrecognized arguments: --exchange-json" in prepared.stderr:
            prepared = prepare(command, message.encode("utf-8"))
        if prepared.returncode != 0:
            return ExchangeData()
        value = json.loads(prepared.stdout)
        if not isinstance(value, dict):
            return ExchangeData()
        context, system_prompt = value.get("context"), value.get("systemPrompt")
        if not isinstance(context, str) or len(context) > 8000 or "\0" in context:
            return ExchangeData()
        context.encode("utf-8")
        if system_prompt is not None:
            if not isinstance(system_prompt, str) or "\0" in system_prompt:
                return ExchangeData()
            system_prompt.encode("utf-8")
        return ExchangeData(cue_context=context, system_prompt=system_prompt)
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return ExchangeData()


async def intake(home: Path, folder: Path, message: str, earlier_messages: list[str],
                 details: PhaseDetails, execute: Callable[[ExchangeData], Awaitable[End]]) -> End:
    details.enter("intake")
    data = await asyncio.to_thread(prepare_cues, home, folder, message, earlier_messages)
    details.public.cue_context = data.cue_context
    details.public.system_prompt = data.system_prompt
    return await planning(details, execute)


async def planning(details: PhaseDetails, execute: Callable[[ExchangeData], Awaitable[End]]) -> End:
    """Continue to Execution with the public Exchange data."""
    details.enter("planning")
    return await execute(details.public)


def finalization(details: PhaseDetails, outcome: End) -> End:
    """Pass the outcome to the shared Exchange end handling."""
    details.enter("finalization")
    details.finish()
    return outcome
