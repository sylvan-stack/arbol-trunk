"""The history the Trivial Trunk sends its run (TRV-0, "The history it sends"; TRV-D2).

Every earlier Exchange of the chat that was not replaced, whatever its end, in the order of their numbers, and within
each the rows in the order of their positions: the Leather Bag's message, each block of the answer exactly as saved,
and each tool call the agent made itself with its result, in the form of DRV-2. The calls of sub-agents are left out,
as the chat leaves them out, and `result` and `error` are left out where they are NULL.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HistoryRow:
    """A row of `messages` or of `tool_calls`, with the number of its Exchange in the chat."""

    number: int
    position: int
    replaced: bool = False
    role: str | None = None  # a message: user or assistant
    text: str | None = None
    name: str | None = None  # a tool call
    input: Any = None
    ok: bool | None = None
    result: Any = None
    error: str | None = None
    parent_call_id: str | None = None

    @property
    def is_message(self) -> bool:
        return self.role is not None


def make_history(rows: Iterable[HistoryRow], before: int) -> list[dict[str, Any]]:
    """The history items of the Exchanges numbered below `before`."""
    kept = sorted((row for row in rows if row.number < before and not row.replaced
                   and (row.is_message or row.parent_call_id is None)), key=lambda row: (row.number, row.position))
    items: list[dict[str, Any]] = []
    for row in kept:
        if row.is_message:
            items.append({"type": "message", "role": row.role, "text": row.text})
            continue
        item: dict[str, Any] = {"type": "tool_call", "name": row.name, "input": row.input, "ok": row.ok}
        if row.result is not None:
            item["result"] = row.result
        if row.error is not None:
            item["error"] = row.error
        items.append(item)
    return items
