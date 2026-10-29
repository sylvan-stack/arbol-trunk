# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import json
import unittest
from typing import Any

from psycopg.types.json import Jsonb

from arbol_trunk_trivial.rows import RowMaker

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
RUN = f"{X}.1"
STARTED = {"runId": RUN, "seq": 1, "at": "2026-10-15T09:30:01.204Z", "type": "started", "continuity": "fresh",
           "subscriptionId": "anthropic", "model": "sonnet", "effort": "high", "toolVersion": "2.1.294",
           "driverBuild": "b"}
LINES: list[dict[str, Any]] = [  # the example of RCT-1
    STARTED,
    {"runId": RUN, "seq": 2, "at": "2026-10-15T09:30:03.020Z", "type": "text_delta", "text": "Let me "},
    {"runId": RUN, "seq": 3, "at": "2026-10-15T09:30:03.310Z", "type": "text", "text": "Let me read it."},
    {"runId": RUN, "seq": 4, "at": "2026-10-15T09:30:03.400Z", "type": "tool_started", "callId": "call_1",
     "name": "shell", "input": {"command": "cat build.sh"}},
    {"runId": RUN, "seq": 5, "at": "2026-10-15T09:30:03.900Z", "type": "tool_finished", "callId": "call_1",
     "ok": True, "result": {"output": "#!/bin/sh\nset -e\n…", "exitCode": 0}},
    {"runId": RUN, "seq": 6, "at": "2026-10-15T09:30:09.700Z", "type": "text",
     "text": "It compiles the three packages and copies them to dist/."},
    {"runId": RUN, "seq": 7, "at": "2026-10-15T09:30:09.800Z", "type": "finished", "outcome": "completed",
     "usage": {"model": "sonnet", "inputTokens": 5120, "outputTokens": 812}, "producedOutput": True,
     "unfinishedCalls": []},
]


def plain(value: Any) -> Any:
    return json.loads(json.dumps(value, default=lambda o: o.obj if isinstance(o, Jsonb) else str(o)))


class Rows(unittest.TestCase):
    def take(self, lines: list[dict[str, Any]]) -> tuple[RowMaker, list[Any]]:
        maker = RowMaker(X)
        rows: list[Any] = []
        for n, event in enumerate(lines, 1):
            rows += maker.take(n, event)
        return maker, rows


ASK = {"callId": "call_2", "questions": [{"id": "branch", "question": "Which branch?", "multiple": False,
                                          "options": [{"label": "main"}, {"label": "dev"}]}]}
MAIN = {"type": "answers", "answers": {"branch": ["main"]}}
DEV = {"type": "answers", "answers": {"branch": ["dev"]}}


def asked(seq: int, kind: str, **fields: Any) -> dict[str, Any]:
    return {"runId": RUN, "seq": seq, "at": "2026-10-15T09:31:00.000Z", "type": kind, **fields}


class Questions(unittest.TestCase):
    """The row of a question holds `ask` and `answer` (RCT-3, "How lines become rows")."""

    def rows(self, lines: list[dict[str, Any] | tuple[str, dict[str, Any]]]) -> tuple[RowMaker, list[Any]]:
        maker = RowMaker(X)
        rows: list[Any] = []
        for n, line in enumerate(lines, 1):
            rows += maker.take_answer(line[1]) if isinstance(line, tuple) else maker.take(n, line)
        return maker, rows

    def opened(self) -> list[dict[str, Any] | tuple[str, dict[str, Any]]]:
        return [asked(1, "tool_started", callId="call_2", name="ask_user", input={"questions": ASK["questions"]}),
                asked(2, "ask_opened", askId="ask_3", ask=ASK)]

    def finish(self, seq: int) -> dict[str, Any]:
        return asked(seq, "tool_finished", callId="call_2", ok=True, result=MAIN)



# Archived complete imports; restore needed names in their original scope, not at this file tail.
