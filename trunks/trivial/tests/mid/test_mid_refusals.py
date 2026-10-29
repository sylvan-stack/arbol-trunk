"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_refusals as _support
from test_refusals import (
    Acceptance,
    Accepted,
    Any,
    CHAT,
    Connect,
    Connection,
    FakeDatabase,
    InvalidInput,
    LAUNCHER,
    NoDriver,
    OPEN,
    Output,
    Path,
    Prepared,
    ROOT_CONTRACTS,
    ROUTE,
    SlowAcceptance,
    SlowConnection,
    StartTest,
    TheDatabaseAtAcceptance,
    TheRootTheKeychainAndTheFolder,
    WholeStart,
    asyncio,
    copy,
    fakes,
    json,
    mock,
    os,
    roots_folder,
    security_stand_in,
    settings_file,
    start,
    tempfile,
    time,
    unittest,
    with_capabilities,
)


class WholeStart(_support.WholeStart):
# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::WholeStart.test_an_accepted_start_answers_with_the_acceptance_line_and_starts_the_driver
    def test_an_accepted_start_answers_with_the_acceptance_line_and_starts_the_driver(self) -> None:
        status, lines = self.start(*ROUTE, "hi")
        self.assertEqual(json.loads(lines[0])["accepted"], True)
        self.assertEqual(len((self.home / "starts").read_text().splitlines()), 1)
        self.assertEqual(status, 1)  # the launcher ended without `finished`: the Exchange failed with driver_failed
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::WholeStart.test_an_accepted_start_answers_with_the_acceptance_line_and_starts_the_driver

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::WholeStart.test_an_unknown_option_is_refused_with_invalid_input
    def test_an_unknown_option_is_refused_with_invalid_input(self) -> None:
        self.refused("invalid_input", *ROUTE, "--bogus", "hi")
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::WholeStart.test_an_unknown_option_is_refused_with_invalid_input



class InvalidInput(_support.InvalidInput):
# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::InvalidInput.test_the_command_line
    def test_the_command_line(self) -> None:
        for args, command in (((*ROUTE, "--bogus", "hi"), "run"), ((*ROUTE, "-v", "4", "hi"), "run"),
                              ((*ROUTE, "hi"), "list"), ((), ""), ((*ROUTE, "--root", "rct", "hi"), "run"),
                              ((*ROUTE, "--model", "opus", "hi"), "run"), ((*ROUTE, "one", "two"), "run"),
                              ((*ROUTE, "--cwd"), "run")):
            with self.subTest(args=args, command=command):
                self.refused("invalid_input", *args, command=command)
        self.assertFalse((self.home / "security.args").exists(), "the Keychain was read")
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::InvalidInput.test_the_command_line

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::InvalidInput.test_a_root_identifier_that_is_not_one_lower_case_word_of_letters_and_digits
    def test_a_root_identifier_that_is_not_one_lower_case_word_of_letters_and_digits(self) -> None:
        for root in ("../rct", "Rct", "r-c-t", "rct/", ""):
            with self.subTest(root=root):
                self.refused("invalid_input", *ROUTE, "hi", root=root)
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::InvalidInput.test_a_root_identifier_that_is_not_one_lower_case_word_of_letters_and_digits

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::InvalidInput.test_no_message
    def test_no_message(self) -> None:
        self.assertEqual(self.refused("invalid_input", *ROUTE), "No message was handed.")
        self.refused("invalid_input", *ROUTE, request={"message": None})
        self.assertFalse((self.home / "security.args").exists(), "the Keychain was read")
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::InvalidInput.test_no_message

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::InvalidInput.test_an_identifier_that_is_not_a_uuid
    def test_an_identifier_that_is_not_a_uuid(self) -> None:
        for args in (("--exchange", "not-a-uuid"), ("--chat", "C3D4E5F6-0718-4293-A4B5-C6D7E8F90A1B"),
                     ("--replaces", "7f3a2c1e")):
            with self.subTest(args=args):
                self.refused("invalid_input", *ROUTE, *args, "hi")
        self.refused("invalid_input", *ROUTE, request={"message": "hi", "exchange": 7})
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::InvalidInput.test_an_identifier_that_is_not_a_uuid

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::InvalidInput.test_a_working_folder_that_is_not_absolute_or_does_not_exist
    def test_a_working_folder_that_is_not_absolute_or_does_not_exist(self) -> None:
        for folder in ("work", "./work", str(self.home / "missing"), str(self.home / "start.json")):
            with self.subTest(folder=folder):
                (self.home / "start.json").write_text("{}")
                self.refused("invalid_input", *ROUTE, "--cwd", folder, "hi")
                self.refused("invalid_input", *ROUTE, request={"message": "hi", "workingFolder": folder})
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::InvalidInput.test_a_working_folder_that_is_not_absolute_or_does_not_exist

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::InvalidInput.test_replaces_together_with_a_message
    def test_replaces_together_with_a_message(self) -> None:
        exchange = "2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"
        self.assertIn("--replaces takes no message", self.refused("invalid_input", *ROUTE, "--replaces", exchange,
                                                                  "hi"))
        self.refused("invalid_input", *ROUTE, request={"replaces": exchange, "message": "hi"})
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::InvalidInput.test_replaces_together_with_a_message

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::InvalidInput.test_a_request_file_that_cannot_be_read_or_holds_no_object
    def test_a_request_file_that_cannot_be_read_or_holds_no_object(self) -> None:
        self.refused("invalid_input", *ROUTE, "--request", str(self.home / "none.json"), "hi")
        for body in ("[1]", "{", '{"route": "claude", "message": "hi"}', '{"message": 4}'):
            with self.subTest(body=body):
                (self.home / "start.json").write_text(body)
                self.refused("invalid_input", "--request", str(self.home / "start.json"))
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::InvalidInput.test_a_request_file_that_cannot_be_read_or_holds_no_object



class NoDriver(_support.NoDriver):
# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::NoDriver.test_no_driver_handed_while_the_settings_file_names_none_names_the_file_and_its_key
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
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::NoDriver.test_no_driver_handed_while_the_settings_file_names_none_names_the_file_and_its_key

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::NoDriver.test_the_driver_of_the_settings_file_is_started_when_none_is_handed
    def test_the_driver_of_the_settings_file_is_started_when_none_is_handed(self) -> None:
        settings_file(self.home).parent.mkdir(parents=True)
        settings_file(self.home).write_text('{"driver": "claude"}')
        status, lines = self.start("hi")
        self.assertEqual(json.loads(lines[0])["accepted"], True)
        self.assertEqual(len((self.home / "starts").read_text().splitlines()), 1)
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::NoDriver.test_the_driver_of_the_settings_file_is_started_when_none_is_handed



class TheRootTheKeychainAndTheFolder(_support.TheRootTheKeychainAndTheFolder):
# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_root_without_a_readable_root_json_is_unknown
    def test_a_root_without_a_readable_root_json_is_unknown(self) -> None:
        self.refused("unknown_root", *ROUTE, "hi", root="nosuch")
        self.assertEqual(os.listdir(roots_folder(self.home)), ["rct"])
        for content in ("{", "[]", '{"rootContract": 1}', '{"database": "arbol_rct", "rootContract": "1"}'):
            with self.subTest(content=content):
                self.root_json(content)
                self.refused("unknown_root", *ROUTE, "hi")
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_root_without_a_readable_root_json_is_unknown

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_root_whose_version_is_not_in_root_contracts_is_a_contract_mismatch
    def test_a_root_whose_version_is_not_in_root_contracts_is_a_contract_mismatch(self) -> None:
        self.assertEqual(ROOT_CONTRACTS, (1,))
        for version in (2, 0, 999):
            with self.subTest(version=version):
                self.root_json({"database": "arbol_rct", "rootContract": version})
                message = self.refused("contract_mismatch", *ROUTE, "hi")
                self.assertIn(f"version {version}", message)
        self.assertFalse((self.home / "security.args").exists(), "the Keychain was read")
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_root_whose_version_is_not_in_root_contracts_is_a_contract_mismatch

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_keychain_read_that_fails_is_refused_naming_the_keychain
    def test_a_keychain_read_that_fails_is_refused_naming_the_keychain(self) -> None:
        self.security = security_stand_in(self.home, status=51)
        message = self.refused("database_unavailable", *ROUTE, "hi")
        self.assertIn("Keychain", message)
        self.assertEqual(self.database.connections, 0)
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_keychain_read_that_fails_is_refused_naming_the_keychain

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_keychain_read_that_gives_no_answer_within_2_seconds_is_refused_naming_the_keychain
    def test_a_keychain_read_that_gives_no_answer_within_2_seconds_is_refused_naming_the_keychain(self) -> None:
        self.security = security_stand_in(self.home, sleep=30)
        began = time.monotonic()
        message = self.refused("database_unavailable", *ROUTE, "hi")
        self.assertLess(time.monotonic() - began, 3.0)
        self.assertIn("Keychain", message)
        self.assertIn("2 seconds", message)
        self.assertEqual(self.database.connections, 0)
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_keychain_read_that_gives_no_answer_within_2_seconds_is_refused_naming_the_keychain

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_folder_that_cannot_be_made_is_trunk_failed_and_leaves_nothing_behind
    def test_a_folder_that_cannot_be_made_is_trunk_failed_and_leaves_nothing_behind(self) -> None:
        os.chmod(self.exchanges, 0o500)
        try:
            self.assertIn("folder", self.refused("trunk_failed", *ROUTE, "hi"))
        finally:
            os.chmod(self.exchanges, 0o700)
        self.assertEqual(self.database.connections, 0)
        os.rmdir(self.exchanges)
        self.refused("trunk_failed", *ROUTE, "hi")
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_folder_that_cannot_be_made_is_trunk_failed_and_leaves_nothing_behind



class TheDatabaseAtAcceptance(_support.TheDatabaseAtAcceptance):
# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::TheDatabaseAtAcceptance.test_a_server_that_cannot_be_reached_is_refused_as_unavailable
    def test_a_server_that_cannot_be_reached_is_refused_as_unavailable(self) -> None:
        self.database.fail_connect = 1
        self.assertIn("cannot be reached", self.refused("database_unavailable", *ROUTE, "hi"))
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::TheDatabaseAtAcceptance.test_a_server_that_cannot_be_reached_is_refused_as_unavailable

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::TheDatabaseAtAcceptance.test_work_with_the_database_not_done_within_10_seconds_of_the_start_is_refused_as_unavailable
    def test_work_with_the_database_not_done_within_10_seconds_of_the_start_is_refused_as_unavailable(self) -> None:
        for delay_connect in (True, False):
            with self.subTest(delay_connect=delay_connect):
                self.database = FakeDatabase(delay=60) if delay_connect else SlowAcceptance()
                began = time.monotonic()
                message = self.refused("database_unavailable", *ROUTE, "hi", started=began - 9.5)
                self.assertLess(time.monotonic() - began, 1.5)
                self.assertIn("within 10 seconds of the start", message)
                self.assertEqual(self.database.closed, 0 if delay_connect else 1)
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::TheDatabaseAtAcceptance.test_work_with_the_database_not_done_within_10_seconds_of_the_start_is_refused_as_unavailable

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::TheDatabaseAtAcceptance.test_a_chat_with_an_open_exchange_is_busy_and_the_refusal_names_it
    def test_a_chat_with_an_open_exchange_is_busy_and_the_refusal_names_it(self) -> None:
        self.database.chats[CHAT] = "2026-10-15T09:30:00Z"
        self.database.exchanges[OPEN] = fakes.Exchange(OPEN, CHAT, 1, "open", "trivial", "0", {}, None, "/", None)
        message = self.refused("chat_busy", *ROUTE, "--chat", CHAT, "hi")
        self.assertEqual(message, f"The chat has an Exchange in progress: {OPEN}.")
        self.assertEqual(self.database.closed, 1)
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::TheDatabaseAtAcceptance.test_a_chat_with_an_open_exchange_is_busy_and_the_refusal_names_it

# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::TheDatabaseAtAcceptance.test_a_chat_whose_exchanges_have_ended_takes_the_next_message
    def test_a_chat_whose_exchanges_have_ended_takes_the_next_message(self) -> None:
        self.database.chats[CHAT] = "2026-10-15T09:30:00Z"
        self.database.exchanges[OPEN] = fakes.Exchange(OPEN, CHAT, 1, "failed", "trivial", "0", {}, None, "/", None)
        status, lines = self.start(*ROUTE, "--chat", CHAT, "hi")
        self.assertEqual(json.loads(lines[0])["number"], 2)
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::TheDatabaseAtAcceptance.test_a_chat_whose_exchanges_have_ended_takes_the_next_message
