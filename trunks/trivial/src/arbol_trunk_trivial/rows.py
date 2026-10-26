"""How lines of `events.jsonl` become rows (RCT-3, "How lines become rows").

| Line                                | Row                                                         | Position                   |
|-------------------------------------|-------------------------------------------------------------|----------------------------|
| a `text` event without parentCallId | `messages`, role assistant, the text as the event carried it | the line's n               |
| a `tool_started` event              | `tool_calls`, written with its `tool_finished`              | the n of the tool_started  |
| a `finished` event                  | `runs`, kind agent, with its usage and its `started` event  | —                          |

The row of a question also holds `ask` from the `ask_opened` that names its call, and `answer` from the last `answer`
line for that question that no `control_refused` for it follows. Every row is written with an insert that does nothing
when the row is already there. At the end, a call without its
`tool_finished` is written as interrupted, and a run without its `finished` as interrupted, with its last usage and the
time of its last line.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from psycopg.types.json import Jsonb

from .storage import stored

INTERRUPTED_CALL = "The Exchange ended before the tool call finished."

Statement = tuple[str, tuple[Any, ...]]


def jsonb(value: Any) -> Jsonb | None:
    return None if value is None else Jsonb(value)


def moment(value: Any) -> datetime:
    """A time of an event, or now when it carries none that can be read."""
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).astimezone(UTC)
        except ValueError:
            pass
    return datetime.now(UTC)


@dataclass(frozen=True)
class MessageRow:
    exchange: str
    position: int
    text: str

    def statement(self) -> Statement:
        return ("INSERT INTO messages (exchange_id, position, role, text) VALUES (%s, %s, 'assistant', %s)"
                " ON CONFLICT DO NOTHING", stored((self.exchange, self.position, self.text)))


@dataclass(frozen=True)
class ToolCallRow:
    exchange: str
    position: int
    run_id: str
    call_id: str
    parent_call_id: str | None
    name: str
    input: Any
    ok: bool
    result: Any = None
    error: str | None = None
    truncated: bool = False
    interrupted: bool = False
    ask: Any = None
    answer: Any = None

    def statement(self) -> Statement:
        return ("INSERT INTO tool_calls (exchange_id, position, run_id, call_id, parent_call_id, name, input, ok,"
                " result, error, truncated, interrupted, ask, answer)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                stored((self.exchange, self.position, self.run_id, self.call_id, self.parent_call_id, self.name,
                 Jsonb(self.input), self.ok, jsonb(self.result), self.error, self.truncated, self.interrupted,
                 jsonb(self.ask), jsonb(self.answer))))


@dataclass(frozen=True)
class RunRow:
    exchange: str
    run_id: str
    kind: str
    outcome: str
    usage: dict[str, Any]
    error: Any
    started: Any
    ended_at: datetime
    line: int = 0

    def statement(self) -> Statement:
        return ("INSERT INTO runs (exchange_id, run_id, kind, outcome, usage, error, started, ended_at)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                stored((self.exchange, self.run_id, self.kind, self.outcome, Jsonb(self.usage), jsonb(self.error),
                 jsonb(self.started), self.ended_at)))


Row = MessageRow | ToolCallRow | RunRow


def row_line(row: Row) -> int:
    return row.line if isinstance(row, RunRow) else row.position


def text(value: Any) -> str | None:
    return value if isinstance(value, str) else None


class RowMaker:
    """Follows the lines of one Exchange's `events.jsonl` and gives the rows each line makes due."""

    def __init__(self, exchange: str) -> None:
        self.exchange = exchange
        self.calls: dict[tuple[str, str], tuple[int, dict[str, Any]]] = {}  # open calls: (runId, callId) to their start
        self.started: dict[str, dict[str, Any]] = {}
        self.usage: dict[str, dict[str, Any]] = {}
        self.last_at: dict[str, Any] = {}
        self.last_n: dict[str, int] = {}
        self.finished: set[str] = set()
        self.seen: list[str] = []  # the runs that gave an event, in order
        self.asks: dict[tuple[str, str], tuple[str, Any]] = {}  # (runId, callId) to the askId and ask of its question
        self.answers: dict[str, Any] = {}  # askId to the answer its last answer line carried

    def take(self, n: int, event: dict[str, Any]) -> list[Row]:
        run_id = text(event.get("runId")) or ""
        kind = event.get("type")
        self.last_n[run_id] = n
        if run_id not in self.seen:
            self.seen.append(run_id)
        if "at" in event:
            self.last_at[run_id] = event["at"]
        if kind == "started":
            self.started[run_id] = event
        elif kind == "usage" and isinstance(event.get("usage"), dict):
            self.usage[run_id] = event["usage"]
        elif kind == "text" and event.get("parentCallId") is None and isinstance(event.get("text"), str):
            return [MessageRow(self.exchange, n, event["text"])]
        elif kind == "tool_started" and isinstance(event.get("callId"), str):
            self.calls[(run_id, event["callId"])] = (n, event)
        elif kind == "ask_opened" and isinstance(event.get("askId"), str) and isinstance(event.get("ask"), dict):
            call = event["ask"].get("callId")
            if isinstance(call, str):
                self.asks[(run_id, call)] = (event["askId"], event["ask"])
        elif kind == "control_refused" and isinstance(event.get("askId"), str):
            self.answers.pop(event["askId"], None)
        elif kind == "tool_finished" and (run_id, event.get("callId")) in self.calls:
            position, started = self.calls.pop((run_id, str(event.get("callId"))))
            ask, answer = self.question(run_id, str(started["callId"]))
            return [ToolCallRow(self.exchange, position, run_id, str(started["callId"]),
                                text(started.get("parentCallId")), str(started.get("name", "")),
                                started.get("input"), event.get("ok") is True, event.get("result"),
                                text(event.get("error")), event.get("truncated") is True,
                                event.get("interrupted") is True, ask, answer)]
        elif kind == "finished" and run_id not in self.finished:
            self.finished.add(run_id)
            said = event.get("outcome")
            outcome = said if isinstance(said, str) and said in ("completed", "failed", "cancelled") else "failed"
            error = event.get("error") if outcome == "failed" else None
            if outcome == "failed" and error is None:
                error = {"code": "internal", "message": "The Driver's finished event said failed without an error."}
            carried = event.get("usage")
            usage: dict[str, Any] = carried if isinstance(carried, dict) else self.usage.get(run_id, {})
            return [RunRow(self.exchange, run_id, "agent", outcome, usage, error, self.started.get(run_id),
                           moment(event.get("at")), n)]
        return []

    def take_answer(self, value: dict[str, Any]) -> list[Row]:
        """An `answer` line handed to the run: it makes no row of its own, and is kept for its question's row."""
        if isinstance(value.get("askId"), str):
            self.answers[value["askId"]] = value.get("answer")
        return []

    def question(self, run_id: str, call_id: str) -> tuple[Any, Any]:
        """The ask and the answer of the question a call carries, (None, None) for any other call."""
        found = self.asks.get((run_id, call_id))
        if found is None:
            return None, None
        ask_id, ask = found
        return ask, self.answers.get(ask_id)

    def at_end(self, run_ids: list[str] | None = None) -> list[Row]:
        """The rows the end makes due: a call without its `tool_finished` as interrupted, and each run that gave an
        event (or each of `run_ids`) without its `finished` as interrupted, with its last usage and the time of its
        last line."""
        rows: list[Row] = []
        for (run_id, call_id), (position, started) in sorted(self.calls.items(), key=lambda item: item[1][0]):
            ask, answer = self.question(run_id, call_id)
            rows.append(ToolCallRow(self.exchange, position, run_id, call_id, text(started.get("parentCallId")),
                                    str(started.get("name", "")), started.get("input"), False,
                                    error=INTERRUPTED_CALL, interrupted=True, ask=ask, answer=answer))
        self.calls.clear()
        for run_id in self.seen if run_ids is None else run_ids:
            if run_id not in self.finished:
                self.finished.add(run_id)
                rows.append(RunRow(self.exchange, run_id, "agent", "interrupted", self.usage.get(run_id, {}), None,
                                   self.started.get(run_id), moment(self.last_at.get(run_id)), self.last_n.get(run_id, 0)))
        return rows
