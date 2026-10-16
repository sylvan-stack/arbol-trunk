"""A whole Exchange, from the message to its end, with a stand-in launcher and the fake database: no database server,
no Driver and no network."""

import asyncio
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from audit import opened_files
from fakes import FakeDatabase
from stand_ins import security_stand_in

from arbol_trunk_trivial.command import handed, parse
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.run import Output, run_exchange
from arbol_trunk_trivial.settings import settings_file
from arbol_trunk_trivial.start import prepare

CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"
FIRST = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
SECOND = "2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"

# The stand-in launcher: it keeps what it was started with and the record beside its request, and plays the events
# of the file named in $STANDIN_EVENTS, with its runId.
LAUNCHER = """#!/bin/sh
log="$STANDIN_LOG"
printf '%s\\n' "$*" >> "$log/starts"
request="$4"
cp "$request" "$log/request-$(wc -l < "$log/starts" | tr -d ' ').json"
cp "$(dirname "$request")/record.json" "$log/record.json"
run=$(sed -n 's/.*"runId":"\\([^"]*\\)".*/\\1/p' "$request")
sed "s/RUN/$run/g" "$STANDIN_EVENTS"
"""

PLAIN = [
    {"runId": "RUN", "seq": 1, "at": "2026-10-15T09:30:01.204Z", "type": "started", "continuity": "fresh",
     "subscriptionId": "anthropic", "model": "sonnet", "toolVersion": "stand-in", "driverBuild": "0"},
    {"runId": "RUN", "seq": 2, "at": "2026-10-15T09:30:03.020Z", "type": "text_delta", "text": "Let me "},
    {"runId": "RUN", "seq": 3, "at": "2026-10-15T09:30:03.310Z", "type": "text", "text": "Let me read it."},
    {"runId": "RUN", "seq": 4, "at": "2026-10-15T09:30:03.400Z", "type": "tool_started", "callId": "call_1",
     "name": "shell", "input": {"command": "cat build.sh"}},
    {"runId": "RUN", "seq": 5, "at": "2026-10-15T09:30:03.900Z", "type": "tool_finished", "callId": "call_1",
     "ok": True, "result": {"output": "#!/bin/sh\n", "exitCode": 0}},
    {"runId": "RUN", "seq": 6, "at": "2026-10-15T09:30:09.700Z", "type": "text", "text": "It sets -e."},
    {"runId": "RUN", "seq": 7, "at": "2026-10-15T09:30:09.800Z", "type": "finished", "outcome": "completed",
     "usage": {"model": "sonnet", "inputTokens": 5120, "outputTokens": 812}, "producedOutput": True,
     "unfinishedCalls": []},
]


class WholeExchange(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(os.path.realpath(folder.name))
        self.root = roots_folder(self.home) / "rct"
        (self.root / "exchanges").mkdir(parents=True)
        (self.root / "root.json").write_text(json.dumps({"database": "arbol_rct", "rootContract": 1}))
        (self.home / ".arbol").mkdir()
        (self.home / ".arbol" / "database.json").write_text(json.dumps({"address": "postgresql://rct@%2Ftmp%2Fx"}))
        self.security = str(security_stand_in(self.home, status=44))
        self.bin = self.home / "bin"
        self.bin.mkdir()
        (self.bin / "arbol-claude-driver").write_text(LAUNCHER)
        os.chmod(self.bin / "arbol-claude-driver", 0o755)
        self.log = self.home / "log"
        self.log.mkdir()
        self.work = self.home / "work"
        self.work.mkdir()
        self.database = FakeDatabase()
        self.events(PLAIN)

    def events(self, events: list[dict[str, Any]]) -> None:
        (self.log / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))

    def run_trunk(self, *args: str, small: dict[str, str] | None = None) -> tuple[int, list[str]]:
        lines: list[str] = []
        request = {"smallCallRoute": small} if small else {}
        file = self.home / "start.json"
        file.write_text(json.dumps(request))
        environment = {"STANDIN_LOG": str(self.log), "STANDIN_EVENTS": str(self.log / "events.jsonl"),
                       "ARBOL_TEST_TIME_SCALE": "10"}
        with mock.patch.dict("os.environ", environment):
            prepared = prepare(handed(parse(["--root", "rct", "run", "--request", str(file), *args]),
                                      started_in=str(self.work)), self.home, self.security)
            status = asyncio.run(run_exchange(
                prepared, self.database.connect(), build="0", process={"pid": 1, "startedAt": "x"},
                started=time.monotonic(), output=Output(lines.append), search_path=f"{self.bin}:/usr/bin:/bin"))
        return status, lines

    def test_a_plain_answer_from_the_message_to_its_end(self) -> None:
        status, lines = self.run_trunk("--exchange", FIRST, "--chat", CHAT, "--driver", "claude", "--subscription",
                                       "anthropic", "--model", "sonnet", "What does build.sh do?")
        self.assertEqual(status, 0)
        self.assertEqual(lines, ['{"accepted":true,"duplicate":false,"root":"rct","exchange":"' + FIRST + '",'
                                 '"chat":"' + CHAT + '","number":1,"trunk":"trivial","build":"0"}'])
        self.assertEqual((self.log / "starts").read_text().splitlines(),
                         [f"run --control --request {self.root}/exchanges/{FIRST}/run-1.json"])
        self.assertEqual(json.loads((self.log / "request-1.json").read_text()), {
            "runId": f"{FIRST}.1", "subscriptionId": "anthropic", "model": "sonnet",
            "workingDirectory": str(self.work), "history": [],
            "input": {"role": "user", "text": "What does build.sh do?"}, "chatSessionId": CHAT, "tools": "all"})
        db = self.database
        self.assertEqual(db.exchanges[FIRST].state, "completed")
        self.assertEqual(db.messages, {(FIRST, 0): ("user", "What does build.sh do?"),
                                       (FIRST, 3): ("assistant", "Let me read it."),
                                       (FIRST, 6): ("assistant", "It sets -e.")})
        self.assertEqual(db.tool_calls[(FIRST, 4)]["name"], "shell")
        run = db.runs[(FIRST, f"{FIRST}.1")]
        self.assertEqual((run["kind"], run["outcome"], run["usage"]["inputTokens"], run["started"]["seq"]),
                         ("agent", "completed", 5120, 1))
        self.assertEqual(os.listdir(self.root / "exchanges"), [])

    def test_the_second_message_of_a_chat_sends_the_first_as_its_history(self) -> None:
        self.run_trunk("--exchange", FIRST, "--chat", CHAT, "--driver", "claude", "What does build.sh do?")
        status, _lines = self.run_trunk("--exchange", SECOND, "--chat", CHAT, "--driver", "claude", "Add --clean.")
        self.assertEqual(status, 0)
        request = json.loads((self.log / "request-2.json").read_text())
        self.assertEqual(request["runId"], f"{SECOND}.1")
        self.assertEqual(request["history"], [
            {"type": "message", "role": "user", "text": "What does build.sh do?"},
            {"type": "message", "role": "assistant", "text": "Let me read it."},
            {"type": "tool_call", "name": "shell", "input": {"command": "cat build.sh"}, "ok": True,
             "result": {"output": "#!/bin/sh\n", "exitCode": 0}},
            {"type": "message", "role": "assistant", "text": "It sets -e."},
        ])
        self.assertEqual(self.database.exchanges[SECOND].number, 2)

    def test_with_a_small_call_route_no_small_call_is_made_and_the_route_stays_as_handed(self) -> None:
        small = {"driver": "claude", "subscription": "anthropic", "model": "haiku"}
        status, _lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi", small=small)
        self.assertEqual(status, 0)
        self.assertEqual(len((self.log / "starts").read_text().splitlines()), 1)
        record = json.loads((self.log / "record.json").read_text())
        self.assertEqual((record["route"], record["smallCallRoute"]), ({"driver": "claude"}, small))
        self.assertEqual(self.database.exchanges[FIRST].small_call_route, small)
        self.assertEqual([run["kind"] for run in self.database.runs.values()], ["agent"])

    def test_the_events_file_holds_every_event_under_n_and_the_end_last(self) -> None:
        self.database.fail_end = 1000  # the folder stays, as when the database is away at the end
        with mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "200"}):
            self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        lines = [json.loads(line) for line in (self.root / "exchanges" / FIRST / "events.jsonl").read_text()
                 .splitlines()]
        self.assertEqual([line["n"] for line in lines], list(range(1, len(PLAIN) + 2)))
        self.assertEqual([line["event"]["seq"] for line in lines[:-1]], [event["seq"] for event in PLAIN])
        self.assertEqual(lines[-1]["end"]["state"], "completed")
        record = json.loads((self.root / "exchanges" / FIRST / "record.json").read_text())
        self.assertEqual(record["end"], lines[-1]["end"])

    def test_a_driver_that_is_not_on_the_search_path_fails_the_exchange_with_driver_failed(self) -> None:
        status, _lines = self.run_trunk("--exchange", FIRST, "--driver", "cluade", "hi")
        self.assertEqual(status, 1)
        error = self.database.exchanges[FIRST].error
        self.assertEqual(error["code"], "driver_failed")
        self.assertIn("arbol-cluade-driver", error["message"])
        self.assertEqual(self.database.runs, {})

    def test_a_driver_that_ends_without_finished_fails_it_and_its_run_is_interrupted(self) -> None:
        self.events(PLAIN[:4])
        status, _lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        self.assertEqual(status, 1)
        self.assertEqual(self.database.exchanges[FIRST].error["code"], "driver_failed")
        self.assertEqual(self.database.runs[(FIRST, f"{FIRST}.1")]["outcome"], "interrupted")
        self.assertTrue(self.database.tool_calls[(FIRST, 4)]["interrupted"])

    def test_a_failed_run_keeps_the_drivers_error_whole(self) -> None:
        error = {"code": "rate_limited", "message": "…", "retryable": True, "retryAfterSeconds": 1800}
        self.events([PLAIN[0], {"runId": "RUN", "seq": 2, "type": "finished", "outcome": "failed", "error": error,
                                "producedOutput": False, "unfinishedCalls": []}])
        status, _lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        self.assertEqual(status, 1)
        self.assertEqual(self.database.exchanges[FIRST].error, error)
        self.assertEqual(len((self.log / "starts").read_text().splitlines()), 1)

    def test_a_whole_start_reads_no_settings_file_but_its_own(self) -> None:
        settings_file(self.home).parent.mkdir(parents=True)
        settings_file(self.home).write_text(json.dumps({"driver": "claude"}))
        (self.home / ".arbol" / "arbol-claude-driver.json").write_text("{}")
        with opened_files() as files:
            self.run_trunk("--exchange", FIRST, "hi")
        outside = sorted({os.path.relpath(file, self.home) for file in files if file.startswith(str(self.home))
                          and f"/exchanges/{FIRST}" not in file and "/exchanges/." not in file})
        self.assertEqual(outside, [".arbol/arbol-trunk/trivial.json", ".arbol/database.json",
                                   "Library/Application Support/Arbol/roots/rct/root.json", "start.json"])


if __name__ == "__main__":
    unittest.main()
