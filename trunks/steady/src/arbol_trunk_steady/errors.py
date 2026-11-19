"""A refusal of `run`: one line `{"error": {"code", "message"}}` on standard output and the exit status 1 (RCT-2)."""

from __future__ import annotations

import json


class Refusal(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def line(self) -> str:
        return json.dumps({"error": {"code": self.code, "message": self.message}}, ensure_ascii=False,
                          separators=(",", ":"))


def invalid(message: str) -> Refusal:
    return Refusal("invalid_input", message)
