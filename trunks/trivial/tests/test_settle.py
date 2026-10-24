import asyncio
import json
import os
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

from fakes import Exchange, FakeDatabase

from arbol_trunk_trivial.command import parse
from arbol_trunk_trivial.errors import Refusal
from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.process import started_at
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.settle import Settlement, open_settlement

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
AT = datetime(2026, 10, 15, 9, 30, tzinfo=UTC)


class SettlementTest(unittest.TestCase):
    def setUp(self) -> None:
        name = tempfile.TemporaryDirectory()
        self.addCleanup(name.cleanup)
        self.home = Path(name.name)
        self.root = roots_folder(self.home) / "rct"
        self.exchanges = self.root / "exchanges"
        self.exchanges.mkdir(parents=True)
        (self.root / "root.json").write_text(json.dumps({"database": "arbol_rct", "rootContract": 1}))
        self.record = {"exchange": X, "process": {"pid": os.getpid(), "startedAt": "2000-01-01T00:00:00Z"},
                       "acceptedAt": AT.isoformat()}
        self.folder = ExchangeFolder.make(self.exchanges, X, self.record)
        self.database = FakeDatabase()
        self.database.exchanges[X] = Exchange(X, "chat", 1, "open", "trivial", "0", {}, None, "/w", AT)

    def open(self) -> Settlement | None:
        return asyncio.run(open_settlement(self.home, "rct", X, connect=self.database.connect()))


class OpeningSettlement(SettlementTest):
    def test_the_command_takes_exactly_one_exchange_uuid(self) -> None:
        command = parse(["--root", "rct", "settle", X])
        self.assertEqual((command.root, command.operation, command.options), ("rct", "settle", {"--exchange": X}))
        for args in (["settle"], ["settle", "../x"], ["settle", X.upper()], ["settle", X, "more"]):
            with self.subTest(args=args), self.assertRaises(Refusal):
                parse(["--root", "rct", *args])

    def test_no_folder_needs_no_database_or_driver_settings(self) -> None:
        self.folder.remove()
        self.assertIsNone(self.open())
        self.assertEqual(self.database.connections, 0)

    def test_a_living_process_is_refused_before_any_database_access(self) -> None:
        self.folder.record["process"]["startedAt"] = started_at()
        (self.folder.path / "record.json").write_text(json.dumps(self.folder.record))
        with self.assertRaises(Refusal) as caught:
            self.open()
        self.assertEqual(caught.exception.code, "alive")
        self.assertEqual(self.database.connections, 0)
        self.assertTrue(self.folder.path.exists())

    def test_a_reused_pid_does_not_count_as_a_living_owner(self) -> None:
        pending = self.open()
        assert pending is not None
        self.assertEqual(pending.stored.state, "open")
        asyncio.run(pending.connection.close())

    def test_an_unavailable_database_keeps_the_folder(self) -> None:
        self.database.fail_connect = 1
        with self.assertRaises(Refusal) as caught:
            self.open()
        self.assertEqual(caught.exception.code, "database_unavailable")
        self.assertTrue(self.folder.path.exists())

    def test_a_database_that_never_answers_is_bounded_and_its_connection_closed(self) -> None:
        self.database.delay = 0.1
        with mock.patch("arbol_trunk_trivial.settle.DATABASE_SECONDS", 0.15), self.assertRaises(Refusal) as caught:
            self.open()
        self.assertEqual(caught.exception.code, "database_unavailable")
        self.assertEqual(self.database.closed, 1)
        self.assertTrue(self.folder.path.exists())

    def test_a_folder_whose_exchange_was_never_accepted_is_removed(self) -> None:
        self.database.exchanges.clear()
        self.assertIsNone(self.open())
        self.assertFalse(self.folder.path.exists())
        self.assertEqual(self.database.closed, 1)
