# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
from unittest import mock

from arbol_trunk_trivial.command import handed, parse
from arbol_trunk_trivial.errors import Refusal

import json
import os
import tempfile
import unittest
from pathlib import Path

EXCHANGE = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"


class CommandLine(unittest.TestCase):


    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class RequestFile(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.work = os.path.realpath(self.folder.name)

    def request(self, value: object) -> str:
        file = Path(self.work) / "start.json"
        file.write_text(json.dumps(value), encoding="utf-8")
        return str(file)


# Archived complete imports; restore needed names in their original scope, not at this file tail.

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/test_command.py::CommandLine.test_without_a_message_the_message_is_none
# Reason: Confirms an obvious optional parser field default with no request merge or failure behavior.
# Source: arbol-trunk@353d3829cc486d354cebf071556047863872dbd1:trunks/trivial/tests/test_command.py
# Retained evidence at review: RequestFile precedence and CLI refusal/start tests exercise missing versus supplied messages.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_without_a_message_the_message_is_none(self) -> None:
#         self.assertIsNone(parse(["--root", "sapling", "run", "--request", "/r.json"]).message)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/test_command.py::RequestFile.test_no_route_is_an_empty_route
# Reason: Confirms an empty default dictionary without exercising routing selection.
# Source: arbol-trunk@353d3829cc486d354cebf071556047863872dbd1:trunks/trivial/tests/test_command.py
# Retained evidence at review: RequestFile override and Start.test_the_route_stays_as_handed_when_the_driver_comes_from_the_settings_file remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_no_route_is_an_empty_route(self) -> None:
#         self.assertEqual(handed(parse(["--root", "rct", "run", "hi"]), started_in=self.work).route, {})
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/test_command.py::CommandLine.test_root_first_then_run_its_options_and_the_message_last
# Reason: Copies a normal Command constructor from parsed flags; richer handed-request and real launch paths already exercise parsing.
# Source: arbol-trunk@353d3829cc486d354cebf071556047863872dbd1:trunks/trivial/tests/test_command.py
# Retained evidence at review: Request-file merge, invalid arguments and launch/stream/lifecycle integration remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_root_first_then_run_its_options_and_the_message_last(self) -> None:
#         command = parse(["--root", "sapling", "run", "--detach", "--exchange", EXCHANGE, "--request", "/r.json",
#                          "--driver=claude", "--model", "sonnet", "What does build.sh do?"])
#         self.assertEqual(command, Command("sapling", {"--exchange": EXCHANGE, "--request": "/r.json",
#                                                       "--driver": "claude", "--model": "sonnet"},
#                                           detach=True, message="What does build.sh do?"))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/test_command.py::RequestFile.test_the_message_on_the_command_line_replaces_the_files
# Reason: Asserts the direct message-precedence assignment with two literal strings.
# Source: arbol-trunk@353d3829cc486d354cebf071556047863872dbd1:trunks/trivial/tests/test_command.py
# Retained evidence at review: Mixed request-file/option merge and actual message dispatch remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_message_on_the_command_line_replaces_the_files(self) -> None:
#         file = self.request({"message": "from the file"})
#         self.assertEqual(handed(parse(["--root", "rct", "run", "--request", file, "from the line"])).message,
#                          "from the line")
# LOW-TIER-SOURCE-END
# LOW-TIER-END
