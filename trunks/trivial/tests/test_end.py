# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import json
import os
import time
from unittest import mock

from fake_driver import MovedClock
from arbol_trunk_trivial.end import End, end_of_run, finish, write_end
from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.rows import MessageRow, Row, RunRow

import asyncio
import tempfile
import unittest
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from fakes import Exchange, FakeDatabase

from arbol_trunk_trivial.end import End, finish
from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.rows import Row
from arbol_trunk_trivial.saver import Saver

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
RATE = {"code": "rate_limited", "message": "…", "retryable": True, "retryAfterSeconds": 1800}


class Ends(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class SavingTheEnd(unittest.TestCase):
    def setUp(self) -> None:
        name = tempfile.TemporaryDirectory()
        self.addCleanup(name.cleanup)
        self.exchanges = Path(name.name)
        self.folder = ExchangeFolder.make(self.exchanges, X, {"exchange": X, "signsOfLife": {}})
        self.database = FakeDatabase()
        self.database.exchanges[X] = Exchange(X, "c", 1, "open", "trivial", "0", {}, None, "/w", datetime.now(UTC))

    def finish(self, unsaved: Sequence[Row], at_end: Sequence[Row], end: End) -> bool:
        async def go() -> bool:
            keeper = Saver(self.database.connect())
            keeper.add(unsaved)
            return await finish(keeper, self.folder, at_end, end)

        return asyncio.run(go())


# Archived complete imports; restore needed names in their original scope, not at this file tail.
