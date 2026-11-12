"""Individually selected top-tier cases. Shared fixtures retain their original paths."""
from __future__ import annotations

import test_settle as _support
from test_settle import (
    Output,
    asyncio,
    json,
)


class SavingSettlement(_support.SavingSettlement):
    def test_two_settlers_both_return_the_stored_state_and_only_one_replays(self) -> None:
        self.database.delay = 0.02
        self.admit_dispatch()
        replies: list[list[str]] = [[], []]

        async def together() -> list[int]:
            return await asyncio.gather(*(self.settle_once(Output(lines.append)) for lines in replies))

        self.assertEqual(asyncio.run(together()), [0, 0])
        self.assertEqual([json.loads(lines[0])["settled"] for lines in replies], ["interrupted", "interrupted"])
        self.assertEqual(self.database.ends, 1)
        self.assertEqual(self.database.connections, self.database.closed)
        self.assertFalse(self.folder.path.exists())
