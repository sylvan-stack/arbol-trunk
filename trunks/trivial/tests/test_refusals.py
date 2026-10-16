"""Refusals of `run`, judged from the command line to the answer (RCT-2, "Accepting a message"): one line
`{"error":{"code","message"}}`, the exit status 1, no folder, no row, and no Driver started. With a home of the test's
own, a stand-in `security`, a stand-in launcher and the fake database: no database server, no Driver and no network."""

import asyncio
import copy
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import fakes
from fakes import FakeDatabase
from stand_ins import security_stand_in

from arbol_trunk_trivial.cli import start
from arbol_trunk_trivial.database import Acceptance, Accepted, Connect, Connection
from arbol_trunk_trivial.root import ROOT_CONTRACTS, roots_folder
from arbol_trunk_trivial.run import Output
from arbol_trunk_trivial.settings import settings_file
from arbol_trunk_trivial.start import Prepared

CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"
OPEN = "6e2f4a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"
ROUTE = ("--driver", "claude", "--subscription", "anthropic", "--model", "sonnet")

# A launcher that only notes that it was started, and ends at once without an event.
LAUNCHER = """#!/bin/sh
printf '%s\\n' "$*" >> "$STANDIN_LOG/starts"
"""


class Start(unittest.TestCase):
    """A home with the Root `rct`, `~/.arbol/database.json`, no Keychain item, the stand-in launcher on the search
    path and the fake database, in which a whole start runs."""

    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(os.path.realpath(folder.name))
        self.root = roots_folder(self.home) / "rct"
        self.exchanges = self.root / "exchanges"
        self.exchanges.mkdir(parents=True)
        self.root_json({"database": "arbol_rct", "rootContract": 1})
        (self.home / ".arbol").mkdir()
        (self.home / ".arbol" / "database.json").write_text(json.dumps({"address": "postgresql://rct@%2Ftmp%2Fx"}))
        self.security = security_stand_in(self.home, status=44)
        self.bin = self.home / "bin"
        self.bin.mkdir()
        (self.bin / "arbol-claude-driver").write_text(LAUNCHER)
        os.chmod(self.bin / "arbol-claude-driver", 0o755)
        self.work = self.home / "work"
        self.work.mkdir()
        self.database = FakeDatabase()

    def root_json(self, value: Any) -> None:
        (self.root / "root.json").write_text(value if isinstance(value, str) else json.dumps(value))

    def start(self, *args: str, request: dict[str, Any] | None = None, root: str = "rct", command: str = "run",
              started: float | None = None) -> tuple[int, list[str]]:
        """`--root <root> <command> [--request <file>] <args>` from the command line to its end; its exit status and
        the lines it wrote on standard output."""
        lines: list[str] = []
        request_args: tuple[str, ...] = ()
        if request is not None:
            file = self.home / "start.json"
            file.write_text(json.dumps(request))
            request_args = ("--request", str(file))

        def connector(_prepared: Prepared) -> Connect:
            return self.database.connect()

        with mock.patch.dict("os.environ", {"STANDIN_LOG": str(self.home), "ARBOL_TEST_TIME_SCALE": "10"}):
            status = asyncio.run(start(
                ["--root", root, command, *request_args, *args], home=self.home,
                started=time.monotonic() if started is None else started, connector=connector,
                security=str(self.security), started_in=str(self.work), output=Output(lines.append),
                search_path=f"{self.bin}:/usr/bin:/bin"))
        return status, lines

    def tables(self) -> dict[str, Any]:
        db = self.database
        return copy.deepcopy({"chats": db.chats, "exchanges": db.exchanges, "messages": db.messages,
                              "tool_calls": db.tool_calls, "runs": db.runs, "saves": db.saves})

    def refused(self, code: str, *args: str, request: dict[str, Any] | None = None, root: str = "rct",
                command: str = "run", started: float | None = None) -> str:
        """Judges a refusal: one line `{"error":{"code","message"}}` with `code`, the exit status 1, no folder, no
        row, and no Driver started. Gives its message."""
        before = self.tables()
        status, lines = self.start(*args, request=request, root=root, command=command, started=started)
        self.assertEqual(len(lines), 1, lines)
        answer = json.loads(lines[0])
        self.assertEqual(list(answer), ["error"], answer)
        self.assertEqual(sorted(answer["error"]), ["code", "message"], answer)
        self.assertEqual(answer["error"]["code"], code, answer)
        self.assertIsInstance(answer["error"]["message"], str)
        self.assertTrue(answer["error"]["message"])
        self.assertEqual(lines[0], json.dumps(answer, ensure_ascii=False, separators=(",", ":")))
        self.assertEqual(status, 1)
        self.assertEqual(os.listdir(self.exchanges) if self.exchanges.exists() else [], [])
        self.assertEqual(self.tables(), before)
        self.assertFalse((self.home / "starts").exists(), "a Driver was started")
        message: str = answer["error"]["message"]
        return message


class WholeStart(Start):
    def test_an_accepted_start_answers_with_the_acceptance_line_and_starts_the_driver(self) -> None:
        status, lines = self.start(*ROUTE, "hi")
        self.assertEqual(json.loads(lines[0])["accepted"], True)
        self.assertEqual(len((self.home / "starts").read_text().splitlines()), 1)
        self.assertEqual(status, 1)  # the launcher ended without `finished`: the Exchange failed with driver_failed

    def test_an_unknown_option_is_refused_with_invalid_input(self) -> None:
        self.refused("invalid_input", *ROUTE, "--bogus", "hi")


class InvalidInput(Start):
    """Refused from the options and the request file alone, before the Root, the settings or the Keychain is read."""

    def setUp(self) -> None:
        super().setUp()
        self.root_json("{")  # a start that read the Root would be refused with unknown_root instead

    def test_the_command_line(self) -> None:
        for args, command in (((*ROUTE, "--bogus", "hi"), "run"), ((*ROUTE, "-v", "4", "hi"), "run"),
                              ((*ROUTE, "hi"), "list"), ((), ""), ((*ROUTE, "--root", "rct", "hi"), "run"),
                              ((*ROUTE, "--model", "opus", "hi"), "run"), ((*ROUTE, "one", "two"), "run"),
                              ((*ROUTE, "--cwd"), "run")):
            with self.subTest(args=args, command=command):
                self.refused("invalid_input", *args, command=command)
        self.assertFalse((self.home / "security.args").exists(), "the Keychain was read")

    def test_a_root_identifier_that_is_not_one_lower_case_word_of_letters_and_digits(self) -> None:
        for root in ("../rct", "Rct", "r-c-t", "rct/", ""):
            with self.subTest(root=root):
                self.refused("invalid_input", *ROUTE, "hi", root=root)

    def test_no_message(self) -> None:
        self.assertEqual(self.refused("invalid_input", *ROUTE), "No message was handed.")
        self.refused("invalid_input", *ROUTE, request={"message": None})
        self.assertFalse((self.home / "security.args").exists(), "the Keychain was read")

    def test_an_identifier_that_is_not_a_uuid(self) -> None:
        for args in (("--exchange", "not-a-uuid"), ("--chat", "C3D4E5F6-0718-4293-A4B5-C6D7E8F90A1B"),
                     ("--replaces", "7f3a2c1e")):
            with self.subTest(args=args):
                self.refused("invalid_input", *ROUTE, *args, "hi")
        self.refused("invalid_input", *ROUTE, request={"message": "hi", "exchange": 7})

    def test_a_working_folder_that_is_not_absolute_or_does_not_exist(self) -> None:
        for folder in ("work", "./work", str(self.home / "missing"), str(self.home / "start.json")):
            with self.subTest(folder=folder):
                (self.home / "start.json").write_text("{}")
                self.refused("invalid_input", *ROUTE, "--cwd", folder, "hi")
                self.refused("invalid_input", *ROUTE, request={"message": "hi", "workingFolder": folder})

    def test_replaces_together_with_a_message(self) -> None:
        exchange = "2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"
        self.assertIn("--replaces takes no message", self.refused("invalid_input", *ROUTE, "--replaces", exchange,
                                                                  "hi"))
        self.refused("invalid_input", *ROUTE, request={"replaces": exchange, "message": "hi"})

    def test_a_request_file_that_cannot_be_read_or_holds_no_object(self) -> None:
        self.refused("invalid_input", *ROUTE, "--request", str(self.home / "none.json"), "hi")
        for body in ("[1]", "{", '{"route": "claude", "message": "hi"}', '{"message": 4}'):
            with self.subTest(body=body):
                (self.home / "start.json").write_text(body)
                self.refused("invalid_input", "--request", str(self.home / "start.json"))


class NoDriver(Start):
    def test_no_driver_handed_while_the_settings_file_names_none_names_the_file_and_its_key(self) -> None:
        for content in (None, "{}", '{"driver": ""}', '{"driver": 1}', "["):
            with self.subTest(content=content):
                if content is not None:
                    settings_file(self.home).parent.mkdir(parents=True, exist_ok=True)
                    settings_file(self.home).write_text(content)
                message = self.refused("invalid_input", "--subscription", "anthropic", "--model", "sonnet", "hi")
                self.assertEqual(message, 'No Driver was handed, and ~/.arbol/arbol-trunk/trivial.json names none '
                                          'under "driver".')
        self.assertFalse((self.home / "security.args").exists(), "the Keychain was read")

    def test_the_driver_of_the_settings_file_is_started_when_none_is_handed(self) -> None:
        settings_file(self.home).parent.mkdir(parents=True)
        settings_file(self.home).write_text('{"driver": "claude"}')
        status, lines = self.start("hi")
        self.assertEqual(json.loads(lines[0])["accepted"], True)
        self.assertEqual(len((self.home / "starts").read_text().splitlines()), 1)


class TheRootTheKeychainAndTheFolder(Start):
    def test_a_root_without_a_readable_root_json_is_unknown(self) -> None:
        self.refused("unknown_root", *ROUTE, "hi", root="nosuch")
        self.assertEqual(os.listdir(roots_folder(self.home)), ["rct"])
        for content in ("{", "[]", '{"rootContract": 1}', '{"database": "arbol_rct", "rootContract": "1"}'):
            with self.subTest(content=content):
                self.root_json(content)
                self.refused("unknown_root", *ROUTE, "hi")

    def test_a_root_whose_version_is_not_in_root_contracts_is_a_contract_mismatch(self) -> None:
        self.assertEqual(ROOT_CONTRACTS, (1,))
        for version in (2, 0, 999):
            with self.subTest(version=version):
                self.root_json({"database": "arbol_rct", "rootContract": version})
                message = self.refused("contract_mismatch", *ROUTE, "hi")
                self.assertIn(f"version {version}", message)
        self.assertFalse((self.home / "security.args").exists(), "the Keychain was read")

    def test_a_keychain_read_that_fails_is_refused_naming_the_keychain(self) -> None:
        self.security = security_stand_in(self.home, status=51)
        message = self.refused("database_unavailable", *ROUTE, "hi")
        self.assertIn("Keychain", message)
        self.assertEqual(self.database.connections, 0)

    def test_a_keychain_read_that_gives_no_answer_within_2_seconds_is_refused_naming_the_keychain(self) -> None:
        self.security = security_stand_in(self.home, sleep=30)
        began = time.monotonic()
        message = self.refused("database_unavailable", *ROUTE, "hi")
        self.assertLess(time.monotonic() - began, 3.0)
        self.assertIn("Keychain", message)
        self.assertIn("2 seconds", message)
        self.assertEqual(self.database.connections, 0)

    def test_a_folder_that_cannot_be_made_is_trunk_failed_and_leaves_nothing_behind(self) -> None:
        os.chmod(self.exchanges, 0o500)
        try:
            self.assertIn("folder", self.refused("trunk_failed", *ROUTE, "hi"))
        finally:
            os.chmod(self.exchanges, 0o700)
        self.assertEqual(self.database.connections, 0)
        os.rmdir(self.exchanges)
        self.refused("trunk_failed", *ROUTE, "hi")


class TheDatabase(Start):
    def test_a_server_that_cannot_be_reached_is_refused_as_unavailable(self) -> None:
        self.database.fail_connect = 1
        self.assertIn("cannot be reached", self.refused("database_unavailable", *ROUTE, "hi"))

    def test_work_with_the_database_not_done_within_10_seconds_of_the_start_is_refused_as_unavailable(self) -> None:
        for delay_connect in (True, False):
            with self.subTest(delay_connect=delay_connect):
                self.database = FakeDatabase(delay=60) if delay_connect else SlowAcceptance()
                began = time.monotonic()
                message = self.refused("database_unavailable", *ROUTE, "hi", started=began - 9.5)
                self.assertLess(time.monotonic() - began, 1.5)
                self.assertIn("within 10 seconds of the start", message)
                self.assertEqual(self.database.closed, 0 if delay_connect else 1)

    def test_a_chat_with_an_open_exchange_is_busy_and_the_refusal_names_it(self) -> None:
        self.database.chats[CHAT] = "2026-10-15T09:30:00Z"
        self.database.exchanges[OPEN] = fakes.Exchange(OPEN, CHAT, 1, "open", "trivial", "0", {}, None, "/", None)
        message = self.refused("chat_busy", *ROUTE, "--chat", CHAT, "hi")
        self.assertEqual(message, f"The chat has an Exchange in progress: {OPEN}.")
        self.assertEqual(self.database.closed, 1)

    def test_a_chat_whose_exchanges_have_ended_takes_the_next_message(self) -> None:
        self.database.chats[CHAT] = "2026-10-15T09:30:00Z"
        self.database.exchanges[OPEN] = fakes.Exchange(OPEN, CHAT, 1, "failed", "trivial", "0", {}, None, "/", None)
        status, lines = self.start(*ROUTE, "--chat", CHAT, "hi")
        self.assertEqual(json.loads(lines[0])["number"], 2)


class SlowAcceptance(FakeDatabase):
    """Connects at once; its acceptance never answers."""

    def connect(self) -> Connect:
        async def connect() -> Connection:
            self.connections += 1
            return SlowConnection(self)

        return connect


class SlowConnection(fakes.FakeConnection):
    async def accept(self, acceptance: Acceptance) -> Accepted:
        await asyncio.sleep(60)
        raise AssertionError("unreachable")


if __name__ == "__main__":
    unittest.main()
