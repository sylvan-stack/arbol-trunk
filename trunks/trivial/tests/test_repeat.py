import asyncio
import copy
import json
import time
from unittest import mock

from fakes import FakeConnection, FakeDatabase
from test_accept import CHAT, AcceptanceHome

from arbol_trunk_trivial.accept import Repeated
from arbol_trunk_trivial.database import Acceptance, Accepted, DuplicateExchange, PriorExchange
from arbol_trunk_trivial.output import Output
from arbol_trunk_trivial.run import run_exchange

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"


class Repeats(AcceptanceHome):
    def test_a_repeat_returns_the_original_acceptance_before_making_any_identifier(self) -> None:
        database = FakeDatabase()
        first = self.accept(database, "--exchange", X, "--chat", CHAT, "original")
        database.exchanges[X].state = "completed"
        database.exchanges[X].trunk, database.exchanges[X].build = "another", "abc"
        before = copy.deepcopy((database.chats, database.exchanges, database.messages))
        with mock.patch("arbol_trunk_trivial.accept.uuid.uuid4", side_effect=AssertionError("An identifier was made")):
            with self.assertRaises(Repeated) as caught:
                self.accept(database, "--exchange", X, "changed input")
        line = json.loads(caught.exception.line)
        self.assertEqual((line["duplicate"], line["exchange"], line["chat"], line["number"], line["trunk"], line["build"]),
                         (True, X, CHAT, 1, "another", "abc"))
        self.assertEqual((database.chats, database.exchanges, database.messages), before)
        self.assertTrue(first.folder.path.exists())

    def test_a_repeat_in_the_database_is_found_at_the_insert_race_too(self) -> None:
        database = FakeDatabase()

        async def raced(connection: FakeConnection, value: Acceptance) -> Accepted:
            raise DuplicateExchange(PriorExchange(X, CHAT, 1, "trivial", "f"))

        with mock.patch.object(FakeConnection, "accept", raced), self.assertRaises(Repeated) as caught:
            self.accept(database, "--exchange", X, "hello")
        self.assertEqual(json.loads(caught.exception.line)["build"], "f")
        self.assertEqual(list(self.exchanges.iterdir()), [])

    def test_a_repeat_from_run_has_only_its_acceptance_and_exit_status_zero(self) -> None:
        database = FakeDatabase()
        first = self.accept(database, "--exchange", X, "hello")
        lines: list[str] = []
        prepared = self.prepared("--driver", "claude", "--exchange", X, "hello")
        status = asyncio.run(run_exchange(prepared, database.connect(), build="0", process={},
                                           started=time.monotonic(), output=Output(lines.append), search_path=""))
        self.assertEqual(status, 0)
        self.assertEqual(len(lines), 1)
        self.assertTrue(json.loads(lines[0])["duplicate"])
        self.assertFalse((first.folder.path / "run-1.json").exists())
