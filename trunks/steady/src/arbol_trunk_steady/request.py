"""The request of the one Driver run, including optional Steady Cue Cards."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .folder import encode, write_file

REQUEST_FILE = "run-1.json"


def run_request(*, exchange: str, chat: str, driver: str, route: dict[str, str], working_folder: str,
                history: list[dict[str, Any]], message: str, cue_context: str | None = None,
                system_prompt: str | None = None) -> dict[str, Any]:
    request: dict[str, Any] = {"runId": f"{exchange}.1"}
    for name, field in (("subscription", "subscriptionId"), ("model", "model"), ("effort", "effort")):
        if name in route:
            request[field] = route[name]
    request["workingDirectory"] = working_folder
    request["history"] = history
    request["input"] = {"role": "user", "text": message}
    request["chatSessionId"] = chat
    if driver in ("claude", "codex"):
        request["arbolChat"] = True
    if cue_context is not None:
        request["cueContext"] = cue_context
        if system_prompt:
            request["systemPrompt"] = system_prompt
    request["tools"] = "all"
    return request


def write_request(folder: Path, request: dict[str, Any]) -> Path:
    """Writes the request into the Exchange's folder with the mode 0600."""
    file = folder / REQUEST_FILE
    write_file(file, encode(request) + b"\n")
    return file
