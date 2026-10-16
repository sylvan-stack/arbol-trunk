import asyncio
import time
import unittest
from datetime import UTC, datetime

from fakes import FakeDatabase

from arbol_trunk_trivial.accept import accept_in_database
from arbol_trunk_trivial.database import Acceptance, Accepted, Connection
from arbol_trunk_trivial.errors import Refusal

CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"
ROUTE = {"driver": "claude", "subscription": "anthropic", "model": "sonnet", "effort": "high"}
SMALL = {"driver": "claude", "subscription": "anthropic", "model": "haiku"}


def acceptance(exchange: str, message: str = "What does build.sh do?", chat: str = CHAT) -> Acceptance:
    return Acceptance(exchange, chat, message, "trivial", "0", ROUTE, SMALL, "/Users/sam/repos/shop",
                      datetime(2026, 10, 15, 9, 30, tzinfo=UTC))


def accept(database: FakeDatabase, value: Acceptance, seconds: float = 10.0) -> tuple[Connection, Accepted]:
    return asyncio.run(accept_in_database(database.connect(), value, time.monotonic() + seconds))


class Acceptances(unittest.TestCase):
    def test_the_chat_the_open_exchange_and_the_message_at_position_0(self) -> None:
        database = FakeDatabase()
        _connection, accepted = accept(database, acceptance("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"))
        self.assertEqual((accepted.number, accepted.history), (1, []))
        exchange = database.exchanges["7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"]
        self.assertEqual((exchange.chat, exchange.number, exchange.state, exchange.route, exchange.small_call_route,
                          exchange.working_folder), (CHAT, 1, "open", ROUTE, SMALL, "/Users/sam/repos/shop"))
        self.assertEqual(database.messages, {("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b", 0):
                                             ("user", "What does build.sh do?")})
        self.assertEqual(list(database.chats), [CHAT])

    def test_the_second_message_gets_the_next_number_and_the_history_of_the_first(self) -> None:
        database = FakeDatabase()
        accept(database, acceptance("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"))
        database.messages[("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b", 3)] = ("assistant", "Let me read it.")
        database.exchanges["7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"].state = "completed"
        _connection, accepted = accept(database, acceptance("2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f", "Add --clean."))
        self.assertEqual(accepted.number, 2)
        self.assertEqual([(row.number, row.position, row.text) for row in accepted.history],
                         [(1, 0, "What does build.sh do?"), (1, 3, "Let me read it.")])

    def test_a_chat_with_an_open_exchange_is_busy_and_names_it(self) -> None:
        database = FakeDatabase()
        accept(database, acceptance("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"))
        with self.assertRaises(Refusal) as caught:
            accept(database, acceptance("2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"))
        self.assertEqual(caught.exception.code, "chat_busy")
        self.assertIn("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b", caught.exception.message)

    def test_work_with_the_database_past_its_deadline_is_refused_as_unavailable(self) -> None:
        database = FakeDatabase(delay=0.3)
        began = time.monotonic()
        with self.assertRaises(Refusal) as caught:
            accept(database, acceptance("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"), seconds=0.4)
        self.assertEqual(caught.exception.code, "database_unavailable")
        self.assertLess(time.monotonic() - began, 1.0)

    def test_a_database_that_cannot_be_reached_is_refused_as_unavailable(self) -> None:
        with self.assertRaises(Refusal) as caught:
            accept(FakeDatabase(fail_connect=1), acceptance("7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"))
        self.assertEqual(caught.exception.code, "database_unavailable")


if __name__ == "__main__":
    unittest.main()
