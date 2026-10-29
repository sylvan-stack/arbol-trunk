"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_accept as _support
# from test_accept import (
#     Acceptance,
#     AcceptanceHome,
#     Acceptances,
#     Accepted,
#     AcceptingAMessage,
#     CHAT,
#     Connection,
#     Exchange,
#     FakeDatabase,
#     Path,
#     Prepared,
#     ROUTE,
#     SMALL,
#     UTC,
#     accept,
#     accept_in_database,
#     accept_message,
#     acceptance,
#     asyncio,
#     datetime,
#     handed,
#     json,
#     os,
#     parse,
#     prepare,
#     roots_folder,
#     security_stand_in,
#     tempfile,
#     time,
#     unittest,
# )


# class Acceptances(_support.Acceptances):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_accept.py::Acceptances.test_the_chat_the_open_exchange_and_the_message_at_position_0
#     def test_the_chat_the_open_exchange_and_the_message_at_position_0(self) -> None:
#         database = FakeDatabase()
#         _connection, accepted = accept(database, acceptance("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"))
#         self.assertEqual((accepted.number, accepted.history), (1, []))
#         exchange = database.exchanges["7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"]
#         self.assertEqual((exchange.chat, exchange.number, exchange.state, exchange.route, exchange.small_call_route,
#                           exchange.working_folder), (CHAT, 1, "open", ROUTE, SMALL, "/Users/sam/repos/shop"))
#         self.assertEqual(database.messages, {("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b", 0):
#                                              ("user", "What does build.sh do?")})
#         self.assertEqual(list(database.chats), [CHAT])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_accept.py::Acceptances.test_the_chat_the_open_exchange_and_the_message_at_position_0

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_accept.py::Acceptances.test_the_second_message_gets_the_next_number_and_the_history_of_the_first
#     def test_the_second_message_gets_the_next_number_and_the_history_of_the_first(self) -> None:
#         database = FakeDatabase()
#         accept(database, acceptance("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"))
#         database.messages[("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b", 3)] = ("assistant", "Let me read it.")
#         database.exchanges["7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"].state = "completed"
#         _connection, accepted = accept(database, acceptance("2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f", "Add --clean."))
#         self.assertEqual(accepted.number, 2)
#         self.assertEqual([(row.number, row.position, row.text) for row in accepted.history],
#                          [(1, 0, "What does build.sh do?"), (1, 3, "Let me read it.")])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_accept.py::Acceptances.test_the_second_message_gets_the_next_number_and_the_history_of_the_first

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_accept.py::Acceptances.test_a_chat_with_an_open_exchange_is_busy_and_names_it
#     def test_a_chat_with_an_open_exchange_is_busy_and_names_it(self) -> None:
#         database = FakeDatabase()
#         accept(database, acceptance("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"))
#         with self.assertRaises(Refusal) as caught:
#             accept(database, acceptance("2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"))
#         self.assertEqual(caught.exception.code, "chat_busy")
#         self.assertIn("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b", caught.exception.message)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_accept.py::Acceptances.test_a_chat_with_an_open_exchange_is_busy_and_names_it

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_accept.py::Acceptances.test_work_with_the_database_past_its_deadline_is_refused_as_unavailable
#     def test_work_with_the_database_past_its_deadline_is_refused_as_unavailable(self) -> None:
#         database = FakeDatabase(delay=0.3)
#         began = time.monotonic()
#         with self.assertRaises(Refusal) as caught:
#             accept(database, acceptance("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"), seconds=0.4)
#         self.assertEqual(caught.exception.code, "database_unavailable")
#         self.assertLess(time.monotonic() - began, 1.0)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_accept.py::Acceptances.test_work_with_the_database_past_its_deadline_is_refused_as_unavailable

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_accept.py::Acceptances.test_a_database_that_cannot_be_reached_is_refused_as_unavailable
#     def test_a_database_that_cannot_be_reached_is_refused_as_unavailable(self) -> None:
#         with self.assertRaises(Refusal) as caught:
#             accept(FakeDatabase(fail_connect=1), acceptance("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"))
#         self.assertEqual(caught.exception.code, "database_unavailable")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_accept.py::Acceptances.test_a_database_that_cannot_be_reached_is_refused_as_unavailable



# class AcceptingAMessage(_support.AcceptingAMessage):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_accept.py::AcceptingAMessage.test_the_acceptance_line_names_the_exchange_the_chat_its_number_the_trunk_and_the_build
#     def test_the_acceptance_line_names_the_exchange_the_chat_its_number_the_trunk_and_the_build(self) -> None:
#         exchange = self.accept(FakeDatabase(), "--exchange", "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b", "--chat", CHAT,
#                                "What does build.sh do?")
#         self.assertEqual(exchange.line, '{"accepted":true,"duplicate":false,"root":"rct","exchange":'
#                                         '"7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b","chat":'
#                                         '"c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b","number":1,"trunk":"trivial",'
#                                         '"build":"0"}')
#         record = json.loads((self.exchanges / "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b" / "record.json").read_text())
#         self.assertEqual(list(record), ["rootContract", "root", "exchange", "chat", "trunk", "build", "process",
#                                         "route", "workingFolder", "acceptedAt", "signsOfLife"])
#         self.assertEqual(record["route"], {"driver": "claude"})
#         self.assertRegex(record["acceptedAt"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_accept.py::AcceptingAMessage.test_the_acceptance_line_names_the_exchange_the_chat_its_number_the_trunk_and_the_build

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_accept.py::AcceptingAMessage.test_identifiers_are_made_when_none_was_handed
#     def test_identifiers_are_made_when_none_was_handed(self) -> None:
#         line = json.loads(self.accept(FakeDatabase(), "hi").line)
#         uuid4 = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
#         self.assertRegex(line["exchange"], uuid4)
#         self.assertRegex(line["chat"], uuid4)
#         self.assertNotEqual(line["exchange"], line["chat"])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_accept.py::AcceptingAMessage.test_identifiers_are_made_when_none_was_handed

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_accept.py::AcceptingAMessage.test_a_refusal_leaves_no_folder
#     def test_a_refusal_leaves_no_folder(self) -> None:
#         with self.assertRaises(Refusal):
#             self.accept(FakeDatabase(fail_connect=1), "hi")
#         self.assertEqual(os.listdir(self.exchanges), [])
#         with self.assertRaises(Refusal) as caught:
#             self.accept(FakeDatabase())
#         self.assertEqual(caught.exception.code, "invalid_input")
#         self.assertEqual(os.listdir(self.exchanges), [])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_accept.py::AcceptingAMessage.test_a_refusal_leaves_no_folder


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_accept.py:16
# from arbol_trunk_trivial.errors import Refusal
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_accept.py:16

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
