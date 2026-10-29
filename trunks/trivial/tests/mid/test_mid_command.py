"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_command as _support
# from test_command import (
#     CHAT,
#     CommandLine,
#     EXCHANGE,
#     Path,
#     RequestFile,
#     json,
#     os,
#     tempfile,
#     unittest,
# )


# class CommandLine(_support.CommandLine):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_command.py::CommandLine.test_refusals_are_invalid_input
#     def test_refusals_are_invalid_input(self) -> None:
#         for args in (["run", "hi"], ["--root", "../sapling", "run", "hi"], ["--root", "Sapling", "run", "hi"],
#                      ["--root", "sapling"], ["--root", "sapling", "list"], ["--root", "sapling", "run", "--bogus", "hi"],
#                      ["--root", "sapling", "run", "--root", "rct", "hi"], ["--root", "sapling", "run", "--cwd"],
#                      ["--root", "sapling", "run", "one", "two"], ["--root", "sapling", "run", "-v", "4", "hi"],
#                      ["--root", "sapling", "run", "--model", "a", "--model", "b", "hi"]):
#             with self.subTest(args=args), self.assertRaises(Refusal) as caught:
#                 parse(args)
#             self.assertEqual(caught.exception.code, "invalid_input")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_command.py::CommandLine.test_refusals_are_invalid_input



# class RequestFile(_support.RequestFile):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_command.py::RequestFile.test_an_option_replaces_only_its_own_field_of_the_file
#     def test_an_option_replaces_only_its_own_field_of_the_file(self) -> None:
#         file = self.request({"chat": CHAT, "message": "Add a --clean option to it.",
#                              "route": {"driver": "claude", "subscription": "anthropic", "model": "sonnet",
#                                        "effort": "high"},
#                              "smallCallRoute": {"driver": "claude", "subscription": "anthropic", "model": "haiku"},
#                              "workingFolder": self.work, "exchange": EXCHANGE})
#         other = "9b3a2c1e-5c6d-4f70-9a1b-2c3d4e5f6a7b"
#         result = handed(parse(["--root", "sapling", "run", "--exchange", other, "--model", "opus", "--request",
#                                file]))
#         self.assertEqual(result.exchange, other)
#         self.assertEqual(result.chat, CHAT)
#         self.assertEqual(result.message, "Add a --clean option to it.")
#         self.assertEqual(result.route, {"driver": "claude", "subscription": "anthropic", "model": "opus",
#                                         "effort": "high"})
#         self.assertEqual(result.small_call_route, {"driver": "claude", "subscription": "anthropic", "model": "haiku"})
#         self.assertEqual(result.working_folder, self.work)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_command.py::RequestFile.test_an_option_replaces_only_its_own_field_of_the_file

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_command.py::RequestFile.test_the_request_file_is_read_once
#     def test_the_request_file_is_read_once(self) -> None:
#         file = self.request({"message": "hi"})
#         with mock.patch("builtins.open", wraps=open) as opened:
#             handed(parse(["--root", "rct", "run", "--request", file]))
#         self.assertEqual([call.args[0] for call in opened.call_args_list].count(file), 1)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_command.py::RequestFile.test_the_request_file_is_read_once

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_command.py::RequestFile.test_the_working_folder_is_the_cwd_option_else_the_folder_it_was_started_from
#     def test_the_working_folder_is_the_cwd_option_else_the_folder_it_was_started_from(self) -> None:
#         file = self.request({"workingFolder": "/"})
#         self.assertEqual(handed(parse(["--root", "rct", "run", "--cwd", self.work, "--request", file, "hi"]))
#                          .working_folder, self.work)
#         self.assertEqual(handed(parse(["--root", "rct", "run", "hi"]), started_in=self.work).working_folder,
#                          self.work)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_command.py::RequestFile.test_the_working_folder_is_the_cwd_option_else_the_folder_it_was_started_from

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_command.py::RequestFile.test_refusals_are_invalid_input
#     def test_refusals_are_invalid_input(self) -> None:
#         cases = [
#             (["--cwd", "relative/folder", "hi"], None),
#             (["--cwd", self.work + "/missing", "hi"], None),
#             (["--exchange", "not-a-uuid", "hi"], None),
#             (["--chat", CHAT.upper(), "hi"], None),
#             (["--request", self.work + "/none.json", "hi"], None),
#             (["hi"], {"route": {"driver": 1}}),
#             (["hi"], {"route": "claude"}),
#             (["hi"], {"smallCallRoute": "claude"}),
#             ([], {"message": 4}),
#             ([], [1, 2]),
#         ]
#         for options, body in cases:
#             args = ["--root", "rct", "run", *options]
#             if body is not None:
#                 args[3:3] = ["--request", self.request(body)]
#             with self.subTest(args=args), self.assertRaises(Refusal) as caught:
#                 handed(parse(args), started_in=self.work)
#             self.assertEqual(caught.exception.code, "invalid_input")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_command.py::RequestFile.test_refusals_are_invalid_input


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_command.py:6
# from unittest import mock
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_command.py:6

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_command.py:8
# from arbol_trunk_trivial.command import handed, parse
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_command.py:8

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_command.py:9
# from arbol_trunk_trivial.errors import Refusal
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_command.py:9

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
