import asyncio
import copy
import json
from dataclasses import replace
from unittest import mock

from fakes import FakeConnection, FakeDatabase
from test_accept import CHAT, AcceptanceHome

from arbol_trunk_trivial.accept import Repeated
from arbol_trunk_trivial.database import Acceptance, Accepted
from arbol_trunk_trivial.errors import Refusal

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
Y = "2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"
Z = "9b3a2c1e-5c6d-4f70-9a1b-2c3d4e5f6a7b"


class ReplacementHome(AcceptanceHome):
    def original(self) -> FakeDatabase:
        database = FakeDatabase()
        first = self.accept(database, "--exchange", X, "--chat", CHAT, "original message")
        asyncio.run(first.connection.close())
        first.folder.discard()
        original = database.exchanges[X]
        original.state, original.ended_at = "completed", original.accepted_at
        database.messages[(X, 2)] = ("assistant", "discard this answer")
        database.tool_calls[(X, 3)] = {"name": "shell", "input": {"command": "old"}, "ok": True}
        database.runs[(X, "run")] = {"usage": {"inputTokens": 41}}
        return database


class ReplacingAMessage(ReplacementHome):
    def test_replacement_copies_the_chat_and_message_and_discards_only_the_old_transcript(self) -> None:
        database = self.original()
        original = copy.deepcopy(database.exchanges[X])
        old_runs, old_chats = copy.deepcopy((database.runs, database.chats))
        new = self.accept(database, "--exchange", Y, "--replaces", X, "--model", "new-model")
        self.assertEqual((new.chat, new.number, new.message), (CHAT, 2, "original message"))
        self.assertEqual(json.loads((new.folder.path / "record.json").read_text())["chat"], CHAT)
        self.assertEqual(database.exchanges[Y].route["model"], "new-model")
        self.assertEqual(database.exchanges[X], replace(original, replaced_by=Y))
        self.assertEqual(database.messages, {(Y, 0): ("user", "original message")})
        self.assertEqual(database.tool_calls, {})
        self.assertEqual((database.runs, database.chats), (old_runs, old_chats))
        self.assertEqual(set(database.exchanges), {X, Y})
        asyncio.run(new.connection.close())

    def test_unknown_open_nonlast_and_already_replaced_exchanges_are_refused_without_changes(self) -> None:
        for target, state in ((Z, "unknown"), (X, "open"), (X, "nonlast"), (X, "replaced")):
            with self.subTest(state=state):
                database = self.original()
                if state == "open":
                    database.exchanges[X].state = "open"
                elif state == "nonlast":
                    second = self.accept(database, "--exchange", Z, "--chat", CHAT, "next")
                    second.folder.discard()
                    asyncio.run(second.connection.close())
                    database.exchanges[Z].state = "completed"
                elif state == "replaced":
                    database.exchanges[X].replaced_by = Z
                before = copy.deepcopy((database.chats, database.exchanges, database.messages,
                                        database.tool_calls, database.runs))
                with self.assertRaises(Refusal) as caught:
                    self.accept(database, "--exchange", Y, "--replaces", target)
                self.assertEqual(caught.exception.code, "not_found" if state == "unknown" else "cannot_replace")
                self.assertEqual((database.chats, database.exchanges, database.messages,
                                  database.tool_calls, database.runs), before)
                self.assertEqual(list(self.exchanges.iterdir()), [])

    def test_a_different_handed_chat_is_invalid_before_any_identifier_or_folder_is_made(self) -> None:
        database = self.original()
        with (mock.patch("arbol_trunk_trivial.accept.uuid.uuid4", side_effect=AssertionError("new identifier")),
              self.assertRaises(Refusal) as caught):
            self.accept(database, "--chat", Z, "--replaces", X)
        self.assertEqual(caught.exception.code, "invalid_input")
        self.assertEqual(list(self.exchanges.iterdir()), [])
        self.assertIsNone(database.exchanges[X].replaced_by)

    def test_the_transaction_checks_the_target_again_after_the_preliminary_lookup(self) -> None:
        database = self.original()
        original = FakeConnection.accept

        async def changed(connection: FakeConnection, value: Acceptance) -> Accepted:
            database.exchanges[X].state = "open"
            return await original(connection, value)

        with mock.patch.object(FakeConnection, "accept", changed), self.assertRaises(Refusal) as caught:
            self.accept(database, "--exchange", Y, "--replaces", X)
        self.assertEqual(caught.exception.code, "cannot_replace")
        self.assertEqual(list(database.exchanges), [X])
        self.assertIsNone(database.exchanges[X].replaced_by)
        self.assertIn((X, 2), database.messages)
        self.assertEqual(list(self.exchanges.iterdir()), [])
        self.assertEqual(database.connections, database.closed)

    def test_repeating_a_replacement_returns_its_original_acceptance_after_the_old_message_was_deleted(self) -> None:
        database = self.original()
        new = self.accept(database, "--exchange", Y, "--replaces", X)
        asyncio.run(new.connection.close())
        before = copy.deepcopy((database.exchanges, database.messages, database.runs))
        with self.assertRaises(Repeated) as caught:
            self.accept(database, "--exchange", Y, "--replaces", X)
        self.assertEqual(json.loads(caught.exception.line), {**json.loads(new.line), "duplicate": True})
        self.assertEqual((database.exchanges, database.messages, database.runs), before)
