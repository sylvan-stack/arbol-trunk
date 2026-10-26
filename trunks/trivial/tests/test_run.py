"""A whole Exchange, from the message to its end, with a stand-in launcher and the fake database: no database server,
no Driver and no network."""

import asyncio
import json
import os
import tempfile
import time
import unittest
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any
from unittest import mock

from audit import opened_files
from fakes import FakeConnection, FakeDatabase
from stand_ins import security_stand_in, with_capabilities

from arbol_trunk_trivial.command import handed, parse
from arbol_trunk_trivial.database import RowRejected
from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.rows import MessageRow, Row
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

# A launcher that starts a shell call and waits for a line on its control input; on a stop line it finishes the call as
# interrupted and the run as cancelled, as a Driver does (DRV-2), and keeps the line it got.
STOPPABLE = """#!/bin/sh
run=$(sed -n 's/.*"runId":"\\([^"]*\\)".*/\\1/p' "$4")
printf '%s\\n' '{"runId":"'"$run"'","seq":1,"type":"started","continuity":"fresh","subscriptionId":"s","toolVersion":"t","driverBuild":"0"}'
printf '%s\\n' '{"runId":"'"$run"'","seq":2,"type":"tool_started","callId":"call_1","name":"shell","input":{"command":"make"}}'
IFS= read -r line
printf '%s\\n' "$line" > "$STANDIN_LOG/control"
printf '%s\\n' '{"runId":"'"$run"'","seq":3,"type":"tool_finished","callId":"call_1","ok":false,"error":"Stopped.","interrupted":true}'
printf '%s\\n' '{"runId":"'"$run"'","seq":4,"type":"finished","outcome":"cancelled","producedOutput":false,"unfinishedCalls":[]}'
"""


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
        (self.bin / "arbol-claude-driver").write_text(with_capabilities(LAUNCHER))
        os.chmod(self.bin / "arbol-claude-driver", 0o755)
        self.log = self.home / "log"
        self.log.mkdir()
        self.work = self.home / "work"
        self.work.mkdir()
        self.database = FakeDatabase()
        self.events(PLAIN)

    def events(self, events: list[dict[str, Any]]) -> None:
        (self.log / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))

    def test_retired_subscription_never_starts_inference(self) -> None:
        status, _ = self.run_trunk("--exchange", FIRST, "--chat", CHAT, "--driver", "claude",
                                   "--subscription", "zai", "hello")
        self.assertEqual(status, 1)
        self.assertFalse((self.log / "starts").exists())
        self.assertEqual(self.database.exchanges[FIRST].error["code"], "driver_failed")
        self.assertEqual(self.database.runs, {})

    def test_pending_migration_never_starts_inference(self) -> None:
        (self.home / ".arbol/pi-cutover.json").write_text(json.dumps({
            "phase": "publishing", "blockedRoutes": [{"driver": "claude", "subscription": "anthropic"}]}))
        status, _ = self.run_trunk("--exchange", FIRST, "--chat", CHAT, "--driver", "claude",
                                   "--subscription", "anthropic", "hello")
        self.assertEqual(status, 1)
        self.assertFalse((self.log / "starts").exists())

    def run_trunk(self, *args: str, small: dict[str, str] | None = None,
                  during: Callable[[], Awaitable[None]] | None = None) -> tuple[int, list[str]]:
        """Runs `run` to its end; `during` runs beside it, from its start."""
        lines: list[str] = []
        request = {"smallCallRoute": small} if small else {}
        file = self.home / "start.json"
        file.write_text(json.dumps(request))
        environment = {"STANDIN_LOG": str(self.log), "STANDIN_EVENTS": str(self.log / "events.jsonl"),
                       "ARBOL_TEST_TIME_SCALE": "10"}
        with mock.patch.dict("os.environ", environment):
            prepared = prepare(handed(parse(["--root", "rct", "run", "--request", str(file), *args]),
                                      started_in=str(self.work)), self.home, self.security)

            async def go() -> int:
                beside = asyncio.ensure_future(during()) if during is not None else None
                status = await run_exchange(
                    prepared, self.database.connect(), build="0", process={"pid": 1, "startedAt": "x"},
                    started=time.monotonic(), output=Output(lines.append), search_path=f"{self.bin}:/usr/bin:/bin")
                if beside is not None:
                    await beside
                return status

            status = asyncio.run(go())
        return status, lines

    def stop_when_the_folder_is_there(self, exchange: str) -> Callable[[], Awaitable[None]]:
        """Appends a stop line to the Exchange's `control` as soon as it is in place, as a writer does (RCT-1.8)."""
        control = self.root / "exchanges" / exchange / "control"

        async def stop() -> None:
            while not control.exists():
                await asyncio.sleep(0.005)
            descriptor = os.open(control, os.O_WRONLY | os.O_APPEND)
            try:
                os.write(descriptor, b'{"type":"stop"}\n')
            finally:
                os.close(descriptor)

        return stop

    def test_a_plain_answer_from_the_message_to_its_end(self) -> None:
        status, lines = self.run_trunk("--exchange", FIRST, "--chat", CHAT, "--driver", "claude", "--subscription",
                                       "anthropic", "--model", "sonnet", "What does build.sh do?")
        self.assertEqual(status, 0)
        self.assertEqual(lines[:1], ['{"accepted":true,"duplicate":false,"root":"rct","exchange":"' + FIRST + '",'
                                 '"chat":"' + CHAT + '","number":1,"trunk":"trivial","build":"0"}'])
        self.assertEqual([json.loads(line)["event"]["seq"] for line in lines[1:-1]],
                         [event["seq"] for event in PLAIN])
        self.assertEqual(json.loads(lines[-1])["end"]["state"], "completed")
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

    def test_foreground_exit_status_follows_the_exchange_end(self) -> None:
        for outcome, expected in (("completed", 0), ("failed", 1), ("cancelled", 2)):
            with self.subTest(outcome=outcome):
                self.database = FakeDatabase()
                end = {**PLAIN[-1], "outcome": outcome}
                if outcome == "failed":
                    end["error"] = {"code": "internal", "message": "The stand-in failed."}
                self.events([*PLAIN[:-1], end])
                status, lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hello")
                self.assertEqual(status, expected)
                self.assertEqual(json.loads(lines[-1])["end"]["state"], outcome)

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
        for driver in ("cluade", "some/path"):
            with self.subTest(driver=driver):
                self.database = FakeDatabase()
                status, _lines = self.run_trunk("--exchange", FIRST, "--driver", driver, "hi")
                self.assertEqual(status, 1)
                error = self.database.exchanges[FIRST].error
                self.assertEqual(error["code"], "driver_failed")
                self.assertIn(f"arbol-{driver}-driver", error["message"])
                self.assertEqual(self.database.runs, {})

    def test_a_driver_that_ends_without_finished_fails_it_and_its_run_is_interrupted(self) -> None:
        self.events(PLAIN[:4])
        status, _lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        self.assertEqual(status, 1)
        self.assertEqual(self.database.exchanges[FIRST].error["code"], "driver_failed")
        self.assertEqual(self.database.runs[(FIRST, f"{FIRST}.1")]["outcome"], "interrupted")
        self.assertTrue(self.database.tool_calls[(FIRST, 4)]["interrupted"])

    def test_a_launchers_refusal_is_kept_in_the_failure_message(self) -> None:
        refusal = """#!/bin/sh
printf '%s\\n' '{"error":{"code":"build_unavailable","message":"No working Build of this Driver."}}'
exit 1
"""
        for query_refused in (True, False):
            with self.subTest(query_refused=query_refused):
                self.database = FakeDatabase()
                (self.bin / "arbol-claude-driver").write_text(
                    refusal if query_refused else with_capabilities(refusal))
                status, _lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
                self.assertEqual(status, 1)
                error = self.database.exchanges[FIRST].error
                self.assertEqual(error["code"], "driver_failed")
                self.assertIn("build_unavailable", error["message"])
                self.assertIn("No working Build of this Driver.", error["message"])
                self.assertFalse((self.log / "starts").exists())

    def test_a_failed_run_keeps_the_drivers_error_whole(self) -> None:
        error = {"code": "rate_limited", "message": "…", "retryable": True, "retryAfterSeconds": 1800}
        self.events([PLAIN[0], {"runId": "RUN", "seq": 2, "type": "finished", "outcome": "failed", "error": error,
                                "producedOutput": False, "unfinishedCalls": []}])
        status, _lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        self.assertEqual(status, 1)
        self.assertEqual(self.database.exchanges[FIRST].error, error)
        self.assertEqual(len((self.log / "starts").read_text().splitlines()), 1)

    def test_a_refusal_can_be_the_only_event_and_no_other_route_is_tried(self) -> None:
        for code in ("rate_limited", "not_signed_in"):
            with self.subTest(code=code):
                self.database = FakeDatabase()
                (self.log / "starts").unlink(missing_ok=True)
                error = {"code": code, "message": "The selected route refused.", "retryable": True,
                         "retryAfterSeconds": 1800, "details": {"route": "original"}}
                self.events([{"runId": "RUN", "seq": 1, "type": "finished", "outcome": "failed", "error": error,
                              "producedOutput": False, "unfinishedCalls": []}])
                status, lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi",
                                               small={"driver": "other", "model": "fallback"})
                self.assertEqual(status, 1)
                self.assertEqual(self.database.exchanges[FIRST].error, error)
                self.assertEqual(json.loads(lines[-1])["end"]["error"], error)
                self.assertEqual(self.database.runs[(FIRST, f"{FIRST}.1")]["error"], error)
                self.assertEqual(len((self.log / "starts").read_text().splitlines()), 1)

    def test_after_a_stop_line_before_the_run_no_run_starts_and_the_exchange_is_cancelled(self) -> None:
        self.database.delay = 0.3  # the acceptance takes a while; the stop line comes meanwhile
        status, lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi",
                                       during=self.stop_when_the_folder_is_there(FIRST))
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(lines[0])["accepted"], True)
        self.assertFalse((self.log / "starts").exists())
        self.assertEqual(self.database.exchanges[FIRST].state, "cancelled")
        self.assertEqual(self.database.runs, {})
        self.assertEqual(os.listdir(self.root / "exchanges"), [])

    def test_a_stop_line_while_a_tool_call_runs_cancels_the_exchange_and_saves_the_call_as_interrupted(self) -> None:
        (self.bin / "arbol-claude-driver").write_text(with_capabilities(STOPPABLE))
        folder = self.root / "exchanges" / FIRST
        written: list[float] = []

        async def stop_once_the_call_runs() -> None:
            while b"tool_started" not in ((folder / "events.jsonl").read_bytes() if folder.exists() else b""):
                await asyncio.sleep(0.005)
            descriptor = os.open(folder / "control", os.O_WRONLY | os.O_APPEND)
            try:
                os.write(descriptor, b'{"type": "stop"}\n')
            finally:
                os.close(descriptor)
            written.append(time.monotonic())

        status, _lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi",
                                        during=stop_once_the_call_runs)
        ended = time.monotonic()
        self.assertEqual(status, 2)
        self.assertEqual((self.log / "control").read_text(), '{"type": "stop"}\n')
        self.assertLess(ended - written[0], 1.8)  # the 18 seconds of RCT-2.7, divided by the time scale of 10
        self.assertEqual(self.database.exchanges[FIRST].state, "cancelled")
        call = self.database.tool_calls[(FIRST, 2)]
        self.assertEqual((call["name"], call["ok"], call["interrupted"]), ("shell", False, True))
        self.assertEqual(self.database.runs[(FIRST, f"{FIRST}.1")]["outcome"], "cancelled")
        self.assertEqual(os.listdir(self.root / "exchanges"), [])

    def test_a_failed_events_write_stops_the_driver_saves_held_rows_and_leaves_the_folder(self) -> None:
        (self.bin / "arbol-claude-driver").write_text(with_capabilities(STOPPABLE))
        append = EventsFile._append

        def fail(file: EventsFile, data: bytes) -> None:
            if file.error is None and b'tool_started' in data:
                file.error = PermissionError("The file became read-only.")
                raise file.error
            append(file, data)

        with mock.patch.object(EventsFile, "_append", fail):
            status, lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        self.assertEqual(status, 1)
        self.assertEqual((self.log / "control").read_text(), '{"type":"stop"}\n')
        self.assertEqual(self.database.exchanges[FIRST].error["code"], "folder_unwritable")
        self.assertTrue(self.database.tool_calls[(FIRST, 2)]["interrupted"])
        self.assertEqual(self.database.runs[(FIRST, f"{FIRST}.1")]["outcome"], "cancelled")
        folder = self.root / "exchanges" / FIRST
        self.assertEqual(len((folder / "events.jsonl").read_text().splitlines()), 1)
        self.assertNotIn("end", json.loads((folder / "record.json").read_text()))
        self.assertFalse(any('"end"' in line for line in lines))

    def test_a_failed_heartbeat_stops_the_driver_and_preserves_rows_already_held(self) -> None:
        (self.bin / "arbol-claude-driver").write_text(with_capabilities(STOPPABLE))
        update = ExchangeFolder.update

        def fail(folder: ExchangeFolder, **fields: Any) -> None:
            if (folder.path / "events.jsonl").stat().st_size > 0:
                raise PermissionError("The folder became read-only.")
            update(folder, **fields)

        with mock.patch.object(ExchangeFolder, "update", fail):
            status, _ = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        self.assertEqual(status, 1)
        self.assertEqual((self.log / "control").read_text(), '{"type":"stop"}\n')
        self.assertEqual(self.database.exchanges[FIRST].error["code"], "folder_unwritable")
        self.assertTrue(self.database.tool_calls[(FIRST, 2)]["interrupted"])
        self.assertTrue((self.root / "exchanges" / FIRST).is_dir())

    def test_a_failed_request_write_never_starts_a_driver_and_ends_directly_in_the_database(self) -> None:
        with mock.patch("arbol_trunk_trivial.run.write_request", side_effect=PermissionError("No write access.")):
            status, _ = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        self.assertEqual(status, 1)
        self.assertFalse((self.log / "starts").exists())
        self.assertEqual(self.database.exchanges[FIRST].error["code"], "folder_unwritable")
        self.assertTrue((self.root / "exchanges" / FIRST).is_dir())

    def test_a_refused_row_stops_the_driver_and_fails_the_exchange_naming_its_line(self) -> None:
        script = STOPPABLE.replace("IFS= read -r line", """printf '%s\\n' '{"runId":"'"$run"'","seq":3,"type":"text","text":"bad row"}'
IFS= read -r line""")
        (self.bin / "arbol-claude-driver").write_text(with_capabilities(script))
        save = FakeConnection.save
        refused: list[int] = []

        async def reject(connection: FakeConnection, row: Row) -> None:
            if isinstance(row, MessageRow) and row.text == "bad row":
                refused.append(row.position)
                raise RowRejected(row)
            await save(connection, row)

        with mock.patch.object(FakeConnection, "save", reject):
            status, lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        self.assertEqual(status, 1)
        self.assertEqual(refused, [3])
        self.assertEqual(self.database.exchanges[FIRST].error["code"], "trunk_failed")
        self.assertIn("line 3", self.database.exchanges[FIRST].error["message"])
        self.assertEqual(json.loads(lines[-1])["end"]["error"], self.database.exchanges[FIRST].error)
        self.assertTrue(self.database.tool_calls[(FIRST, 2)]["interrupted"])
        self.assertEqual((self.log / "control").read_text(), '{"type":"stop"}\n')
        self.assertEqual(os.listdir(self.root / "exchanges"), [])

    def test_a_full_file_fails_the_exchange_and_keeps_only_rows_from_written_lines(self) -> None:
        with mock.patch("arbol_trunk_trivial.events.FILE_BYTES", 500):
            status, raw = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        lines = [json.loads(line) for line in raw[1:]]
        self.assertEqual(status, 1)
        self.assertEqual(lines[-1]["end"]["error"]["code"], "events_file_full")
        self.assertEqual(self.database.exchanges[FIRST].error["code"], "events_file_full")
        self.assertEqual([line["n"] for line in lines], list(range(1, len(lines) + 1)))
        written = {line["n"] for line in lines if line.get("event", {}).get("type") == "tool_started"}
        self.assertTrue({position for exchange, position in self.database.tool_calls if exchange == FIRST} <= written)
        self.assertEqual(self.database.messages, {(FIRST, 0): ("user", "hi"), **{
            (FIRST, line["n"]): ("assistant", line["event"]["text"]) for line in lines
            if line.get("event", {}).get("type") == "text"}})
        self.assertEqual(os.listdir(self.root / "exchanges"), [])

    def test_an_end_that_is_the_first_line_past_the_limit_is_itself_failed(self) -> None:
        event = {"type": "finished", "runId": "RUN", "seq": 1, "outcome": "completed"}
        self.events([event])
        written = '{"n":1,"event":' + json.dumps({**event, "runId": f"{FIRST}.1"}) + '}\n'
        with mock.patch("arbol_trunk_trivial.events.FILE_BYTES", len(written.encode()) + 1):
            status, lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(lines[-1])["end"]["error"]["code"], "events_file_full")
        self.assertEqual(self.database.exchanges[FIRST].state, "failed")

    def test_a_silent_run_is_stopped_and_the_exchange_fails_with_its_own_cause(self) -> None:
        for cooperative in (True, False):
            with self.subTest(cooperative=cooperative):
                self.database = FakeDatabase()
                script = """#!/bin/sh
run=$(sed -n 's/.*"runId":"\\([^\"]*\\)".*/\\1/p' "$4")
printf '%s\\n' '{"runId":"'"$run"'","seq":1,"type":"started"}'
printf '%s\\n' '{"runId":"'"$run"'","seq":2,"type":"text","text":"Half an answer."}'
printf '%s\\n' '{"runId":"'"$run"'","seq":3,"type":"usage","usage":{"inputTokens":2}}'
IFS= read -r line
printf '%s\\n' "$line" > "$STANDIN_LOG/control"
"""
                script += ("""printf '%s\\n' '{"runId":"'"$run"'","seq":4,"type":"finished","outcome":"cancelled"}'
""" if cooperative else "exec /bin/sleep 30\n")
                (self.bin / "arbol-claude-driver").write_text(with_capabilities(script))
                began = time.monotonic()
                with mock.patch("arbol_trunk_trivial.run.SILENCE_SECONDS", 3):
                    status, lines = self.run_trunk("--exchange", FIRST, "--driver", "claude", "hi")
                self.assertLess(time.monotonic() - began, 4)
                self.assertEqual(status, 1)
                self.assertEqual((self.log / "control").read_text(), '{"type":"stop"}\n')
                self.assertEqual(self.database.exchanges[FIRST].error["code"], "driver_silent")
                self.assertEqual(json.loads(lines[-1])["end"]["error"]["code"], "driver_silent")
                run = self.database.runs[(FIRST, f"{FIRST}.1")]
                self.assertEqual(run["outcome"], "cancelled" if cooperative else "interrupted")
                self.assertEqual(run["usage"], {"inputTokens": 2})
                self.assertEqual(self.database.messages[(FIRST, 2)], ("assistant", "Half an answer."))
                self.assertEqual(os.listdir(self.root / "exchanges"), [])

    def test_a_whole_start_reads_no_settings_file_but_its_own(self) -> None:
        settings_file(self.home).parent.mkdir(parents=True)
        settings_file(self.home).write_text(json.dumps({"driver": "claude"}))
        (self.home / ".arbol" / "arbol-claude-driver.json").write_text("{}")
        with opened_files() as files:
            self.run_trunk("--exchange", FIRST, "hi")
        outside = sorted({os.path.relpath(file, self.home) for file in files if file.startswith(str(self.home))
                          and not os.path.isdir(file)
                          and f"/exchanges/{FIRST}" not in file and "/exchanges/." not in file})
        self.assertEqual(outside, [".arbol/arbol-trunk/trivial.json", ".arbol/database.json", ".arbol/pi-cutover.json",
                                   "Library/Application Support/Arbol/roots/rct/root.json", "start.json"])


if __name__ == "__main__":
    unittest.main()
