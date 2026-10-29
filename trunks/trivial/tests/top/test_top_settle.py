"""Individually selected top-tier cases. Shared fixtures retain their original paths."""
from __future__ import annotations

import test_settle as _support
from test_settle import (
    Output,
    X,
    asyncio,
    json,
    settle_exchange,
)


class SavingSettlement(_support.SavingSettlement):
    def test_two_settlers_both_return_the_stored_state_and_only_one_replays(self) -> None:
        self.database.delay = 0.02
        replies: list[list[str]] = [[], []]

        async def together() -> list[int]:
            return await asyncio.gather(*(settle_exchange(
                self.home, "rct", X, output=Output(lines.append), connect=self.database.connect())
                for lines in replies))

        self.assertEqual(asyncio.run(together()), [0, 0])
        self.assertEqual([json.loads(lines[0])["settled"] for lines in replies], ["interrupted", "interrupted"])
        self.assertEqual(self.database.ends, 1)
        self.assertEqual(self.database.connections, self.database.closed)
        self.assertFalse(self.folder.path.exists())
