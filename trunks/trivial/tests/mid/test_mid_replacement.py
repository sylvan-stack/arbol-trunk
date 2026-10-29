
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_replacement.py::ReplacingAMessage.test_replacement_copies_the_chat_and_message_and_discards_only_the_old_transcript
# Reason: Fake-database mapping/refusal/history tables repeat the unchanged transactional top-tier recheck and retained real R14 replacement competition. Case reviewed: Replacement copies the chat and message and discards only the old transcript.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_replacement.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_replacement.py::ReplacingAMessage.test_unknown_open_nonlast_and_already_replaced_exchanges_are_refused_without_changes
# Reason: Fake-database mapping/refusal/history tables repeat the unchanged transactional top-tier recheck and retained real R14 replacement competition. Case reviewed: Unknown open nonlast and already replaced exchanges are refused without changes.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_replacement.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_replacement.py::ReplacingAMessage.test_a_different_handed_chat_is_invalid_before_any_identifier_or_folder_is_made
# Reason: Fake-database mapping/refusal/history tables repeat the unchanged transactional top-tier recheck and retained real R14 replacement competition. Case reviewed: A different handed chat is invalid before any identifier or folder is made.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_replacement.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_different_handed_chat_is_invalid_before_any_identifier_or_folder_is_made(self) -> None:
#         database = self.original()
#         with (mock.patch("arbol_trunk_trivial.accept.uuid.uuid4", side_effect=AssertionError("new identifier")),
#               self.assertRaises(Refusal) as caught):
#             self.accept(database, "--chat", Z, "--replaces", X)
#         self.assertEqual(caught.exception.code, "invalid_input")
#         self.assertEqual(list(self.exchanges.iterdir()), [])
#         self.assertIsNone(database.exchanges[X].replaced_by)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_replacement.py::ReplacingAMessage.test_repeating_a_replacement_returns_its_original_acceptance_after_the_old_message_was_deleted
# Reason: Fake-database mapping/refusal/history tables repeat the unchanged transactional top-tier recheck and retained real R14 replacement competition. Case reviewed: Repeating a replacement returns its original acceptance after the old message was deleted.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_replacement.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_repeating_a_replacement_returns_its_original_acceptance_after_the_old_message_was_deleted(self) -> None:
#         database = self.original()
#         new = self.accept(database, "--exchange", Y, "--replaces", X)
#         asyncio.run(new.connection.close())
#         before = copy.deepcopy((database.exchanges, database.messages, database.runs))
#         with self.assertRaises(Repeated) as caught:
#             self.accept(database, "--exchange", Y, "--replaces", X)
#         self.assertEqual(json.loads(caught.exception.line), {**json.loads(new.line), "duplicate": True})
#         self.assertEqual((database.exchanges, database.messages, database.runs), before)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_replacement.py::ReplacementHistory.test_replacement_and_the_next_message_keep_earlier_history_but_none_of_the_replaced_exchange
# Reason: Fake-database mapping/refusal/history tables repeat the unchanged transactional top-tier recheck and retained real R14 replacement competition. Case reviewed: Replacement and the next message keep earlier history but none of the replaced exchange.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_replacement.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END
