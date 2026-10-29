"""Individually selected top-tier cases. Shared fixtures retain their original paths."""
from __future__ import annotations

import test_replacement as _support
from test_replacement import (
    Acceptance,
    Accepted,
    FakeConnection,
    Refusal,
    X,
    Y,
    mock,
)


class ReplacingAMessage(_support.ReplacingAMessage):
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
