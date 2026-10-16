"""The request of the one run, `run-1.json` in the Exchange's folder (TRV-0, "The request to the Driver"; TRV-D5).

Exactly these fields, and no other: no system prompt, no limits, no labels, no further folders, no search path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .folder import encode, write_file

REQUEST_FILE = "run-1.json"


def run_request(*, exchange: str, chat: str, route: dict[str, str], working_folder: str,
                history: list[dict[str, Any]], message: str) -> dict[str, Any]:
    request: dict[str, Any] = {"runId": f"{exchange}.1"}
    for name, field in (("subscription", "subscriptionId"), ("model", "model"), ("effort", "effort")):
        if name in route:
            request[field] = route[name]
    request["workingDirectory"] = working_folder
    request["history"] = history
    request["input"] = {"role": "user", "text": message}
    request["chatSessionId"] = chat
    request["tools"] = "all"
    return request


def write_request(folder: Path, request: dict[str, Any]) -> Path:
    """Writes the request into the Exchange's folder with the mode 0600."""
    file = folder / REQUEST_FILE
    write_file(file, encode(request) + b"\n")
    return file
