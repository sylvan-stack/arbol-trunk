"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_replacement as _support
# from test_replacement import (
#     Acceptance,
#     AcceptanceHome,
#     Accepted,
#     CHAT,
#     FakeConnection,
#     FakeDatabase,
#     Refusal,
#     ReplacementHistory,
#     ReplacementHome,
#     ReplacingAMessage,
#     X,
#     Y,
#     Z,
#     asyncio,
#     mock,
# )


# class ReplacingAMessage(_support.ReplacingAMessage):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_replacement.py::ReplacingAMessage.test_replacement_copies_the_chat_and_message_and_discards_only_the_old_transcript
#     def test_replacement_copies_the_chat_and_message_and_discards_only_the_old_transcript(self) -> None:
#         database = self.original()
#         original = copy.deepcopy(database.exchanges[X])
#         old_runs, old_chats = copy.deepcopy((database.runs, database.chats))
#         new = self.accept(database, "--exchange", Y, "--replaces", X, "--model", "new-model")
#         self.assertEqual((new.chat, new.number, new.message), (CHAT, 2, "original message"))
#         self.assertEqual(json.loads((new.folder.path / "record.json").read_text())["chat"], CHAT)
#         self.assertEqual(database.exchanges[Y].route["model"], "new-model")
#         self.assertEqual(database.exchanges[X], replace(original, replaced_by=Y))
#         self.assertEqual(database.messages, {(Y, 0): ("user", "original message")})
#         self.assertEqual(database.tool_calls, {})
#         self.assertEqual((database.runs, database.chats), (old_runs, old_chats))
#         self.assertEqual(set(database.exchanges), {X, Y})
#         asyncio.run(new.connection.close())
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_replacement.py::ReplacingAMessage.test_replacement_copies_the_chat_and_message_and_discards_only_the_old_transcript

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_replacement.py::ReplacingAMessage.test_unknown_open_nonlast_and_already_replaced_exchanges_are_refused_without_changes
#     def test_unknown_open_nonlast_and_already_replaced_exchanges_are_refused_without_changes(self) -> None:
#         for target, state in ((Z, "unknown"), (X, "open"), (X, "nonlast"), (X, "replaced")):
#             with self.subTest(state=state):
#                 database = self.original()
#                 if state == "open":
#                     database.exchanges[X].state = "open"
#                 elif state == "nonlast":
#                     second = self.accept(database, "--exchange", Z, "--chat", CHAT, "next")
#                     second.folder.discard()
#                     asyncio.run(second.connection.close())
#                     database.exchanges[Z].state = "completed"
#                 elif state == "replaced":
#                     database.exchanges[X].replaced_by = Z
#                 before = copy.deepcopy((database.chats, database.exchanges, database.messages,
#                                         database.tool_calls, database.runs))
#                 with self.assertRaises(Refusal) as caught:
#                     self.accept(database, "--exchange", Y, "--replaces", target)
#                 self.assertEqual(caught.exception.code, "not_found" if state == "unknown" else "cannot_replace")
#                 self.assertEqual((database.chats, database.exchanges, database.messages,
#                                   database.tool_calls, database.runs), before)
#                 self.assertEqual(list(self.exchanges.iterdir()), [])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_replacement.py::ReplacingAMessage.test_unknown_open_nonlast_and_already_replaced_exchanges_are_refused_without_changes

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_replacement.py::ReplacingAMessage.test_a_different_handed_chat_is_invalid_before_any_identifier_or_folder_is_made
#     def test_a_different_handed_chat_is_invalid_before_any_identifier_or_folder_is_made(self) -> None:
#         database = self.original()
#         with (mock.patch("arbol_trunk_trivial.accept.uuid.uuid4", side_effect=AssertionError("new identifier")),
#               self.assertRaises(Refusal) as caught):
#             self.accept(database, "--chat", Z, "--replaces", X)
#         self.assertEqual(caught.exception.code, "invalid_input")
#         self.assertEqual(list(self.exchanges.iterdir()), [])
#         self.assertIsNone(database.exchanges[X].replaced_by)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_replacement.py::ReplacingAMessage.test_a_different_handed_chat_is_invalid_before_any_identifier_or_folder_is_made

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_replacement.py::ReplacingAMessage.test_repeating_a_replacement_returns_its_original_acceptance_after_the_old_message_was_deleted
#     def test_repeating_a_replacement_returns_its_original_acceptance_after_the_old_message_was_deleted(self) -> None:
#         database = self.original()
#         new = self.accept(database, "--exchange", Y, "--replaces", X)
#         asyncio.run(new.connection.close())
#         before = copy.deepcopy((database.exchanges, database.messages, database.runs))
#         with self.assertRaises(Repeated) as caught:
#             self.accept(database, "--exchange", Y, "--replaces", X)
#         self.assertEqual(json.loads(caught.exception.line), {**json.loads(new.line), "duplicate": True})
#         self.assertEqual((database.exchanges, database.messages, database.runs), before)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_replacement.py::ReplacingAMessage.test_repeating_a_replacement_returns_its_original_acceptance_after_the_old_message_was_deleted



# class ReplacementHistory(_support.ReplacementHistory):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_replacement.py::ReplacementHistory.test_replacement_and_the_next_message_keep_earlier_history_but_none_of_the_replaced_exchange
#     def test_replacement_and_the_next_message_keep_earlier_history_but_none_of_the_replaced_exchange(self) -> None:
#         database = self.original()
#         second = self.accept(database, "--exchange", Y, "--chat", CHAT, "send this again")
#         second.folder.discard()
#         asyncio.run(second.connection.close())
#         database.exchanges[Y].state = "failed"
#         database.messages[(Y, 2)] = ("assistant", "the discarded answer")
#         database.tool_calls[(Y, 3)] = {"name": "shell", "input": {"command": "discard"}, "ok": True}
#         replacement = self.accept(database, "--exchange", Z, "--replaces", Y)
#         expected = [
#             {"type": "message", "role": "user", "text": "original message"},
#             {"type": "message", "role": "assistant", "text": "discard this answer"},
#             {"type": "tool_call", "name": "shell", "input": {"command": "old"}, "ok": True},
#         ]
#         self.assertEqual(replacement.history, expected)
#         replacement.folder.discard()
#         asyncio.run(replacement.connection.close())
#         database.exchanges[Z].state = "completed"
#         database.messages[(Z, 2)] = ("assistant", "new answer")
#         # Even a stale transcript left behind by an older writer must be excluded by replaced_by.
#         database.messages[(Y, 2)] = ("assistant", "stale discarded text")
#         database.tool_calls[(Y, 3)] = {"name": "shell", "input": {}, "ok": True}
#         next_exchange = self.accept(database, "--chat", CHAT, "next")
#         self.assertEqual(next_exchange.history, expected + [
#             {"type": "message", "role": "user", "text": "send this again"},
#             {"type": "message", "role": "assistant", "text": "new answer"}])
#         asyncio.run(next_exchange.connection.close())
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_replacement.py::ReplacementHistory.test_replacement_and_the_next_message_keep_earlier_history_but_none_of_the_replaced_exchange


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_replacement.py:2
# import copy
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_replacement.py:2

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_replacement.py:3
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_replacement.py:3

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_replacement.py:4
# from dataclasses import replace
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_replacement.py:4

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_replacement.py:10
# from arbol_trunk_trivial.accept import Repeated
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_replacement.py:10

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
