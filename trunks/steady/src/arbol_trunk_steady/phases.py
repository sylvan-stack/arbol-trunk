"""Prepare accepted Exchange data and hand it to the next phase."""

import asyncio
import json
import os
import subprocess
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from .end import End
from .phase_details import ExchangeData, PhaseDetails


def prepared_titles(value: object) -> list[str] | None:
    if isinstance(value, list) and all(isinstance(title, str) and title.strip() and "\0" not in title for title in value):
        return value
    return None


async def prepare_cues(home: Path, folder: Path, message: str, earlier_messages: list[str],
                       details: PhaseDetails) -> ExchangeData:
    """Use Forester's non-hook preparation, falling back to its plain-text interface on older Builds."""
    command = [str(home / ".local/bin/forester"), "cues", "prepare", "--overflow-file", str(folder / "cues.md")]

    async def prepare(arguments: list[str], payload: bytes, original: Any) -> subprocess.CompletedProcess[bytes]:
        cwd = os.getcwd()
        try:
            result: subprocess.CompletedProcess[bytes] = await asyncio.to_thread(
                subprocess.run, arguments, input=payload, cwd=cwd, capture_output=True, timeout=5, check=False)
        except subprocess.TimeoutExpired:
            details.subprocess(arguments, cwd, standard_input=original)
            raise
        details.subprocess(arguments, cwd, standard_input=original)
        return result

    try:
        request = {"message": message, "earlierMessages": earlier_messages}
        payload = json.dumps(request).encode("utf-8")
        prepared = await prepare([*command, "--exchange-json"], payload, request)
        if prepared.returncode == 2 and b"unrecognized arguments: --exchange-json" in prepared.stderr:
            prepared = await prepare(command, message.encode("utf-8"), message)
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
        return ExchangeData(
            cue_context=context, system_prompt=system_prompt,
            glossary_terms=prepared_titles(value.get("glossaryTerms")),
            operational_artifacts=prepared_titles(value.get("operationalArtifacts")),
        )
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return ExchangeData()


async def intake(home: Path, folder: Path, message: str, earlier_messages: list[str],
                 details: PhaseDetails, execute: Callable[[ExchangeData], Awaitable[End]]) -> End:
    details.enter("intake")
    data = await prepare_cues(home, folder, message, earlier_messages, details)
    details.intake_output(data)
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
