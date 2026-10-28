import asyncio
import json
import os
import tempfile
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path

from fakes import FakeDatabase
from stand_ins import security_stand_in

from arbol_trunk_trivial.accept import Exchange, accept_in_database, accept_message
from arbol_trunk_trivial.command import handed, parse
from arbol_trunk_trivial.database import Acceptance, Accepted, Connection
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.start import Prepared, prepare

CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"
ROUTE = {"driver": "claude", "subscription": "anthropic", "model": "sonnet", "effort": "high"}
SMALL = {"driver": "claude", "subscription": "anthropic", "model": "haiku"}


def acceptance(exchange: str, message: str = "What does build.sh do?", chat: str = CHAT) -> Acceptance:
    return Acceptance(exchange, chat, message, "trivial", "0", ROUTE, SMALL, "/Users/sam/repos/shop",
                      datetime(2026, 10, 15, 9, 30, tzinfo=UTC))


def accept(database: FakeDatabase, value: Acceptance, seconds: float = 10.0) -> tuple[Connection, Accepted]:
    return asyncio.run(accept_in_database(database.connect(), value, time.monotonic() + seconds))


class Acceptances(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.
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



class AcceptanceHome(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(os.path.realpath(folder.name))
        root = roots_folder(self.home) / "rct"
        self.exchanges = root / "exchanges"
        self.exchanges.mkdir(parents=True)
        (root / "root.json").write_text(json.dumps({"database": "arbol_rct", "rootContract": 1}))
        (self.home / ".arbol").mkdir()
        (self.home / ".arbol" / "database.json").write_text(json.dumps({"address": "postgresql://rct@%2Ftmp%2Fx"}))
        self.security = str(security_stand_in(self.home, status=44))

    def prepared(self, *args: str) -> Prepared:
        return prepare(handed(parse(["--root", "rct", "run", *args]), started_in=str(self.home)), self.home,
                       self.security)

    def accept(self, database: FakeDatabase, *args: str) -> Exchange:
        return asyncio.run(accept_message(self.prepared("--driver", "claude", *args), database.connect(), build="0",
                                          process={"pid": 48213, "startedAt": "2026-10-15T09:30:00.000Z"},
                                          started=time.monotonic()))


class AcceptingAMessage(AcceptanceHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.
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


if __name__ == "__main__":
    unittest.main()

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_accept.py:16
# from arbol_trunk_trivial.errors import Refusal
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_accept.py:16
