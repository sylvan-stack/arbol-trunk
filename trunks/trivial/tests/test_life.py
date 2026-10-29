# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import asyncio
import json
from unittest import mock

from fake_driver import MovedClock, ScriptedDriver
from fakes import FakeConnection, FakeDatabase
from arbol_trunk_trivial.driver import Line
from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.life import SignsOfLife, waiting_for
from arbol_trunk_trivial.rows import Row, RowMaker
from arbol_trunk_trivial.run import drive
from arbol_trunk_trivial.saver import Saver

import os
import tempfile
import unittest
from pathlib import Path

from fake_driver import MovedClock

from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.life import SignsOfLife

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
AT = "2026-10-26T11:00:00.000Z"


class LifeHome(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.exchanges = Path(temporary.name)
        self.folder = ExchangeFolder.make(self.exchanges, X, {
            "exchange": X, "process": {"pid": os.getpid(), "startedAt": AT},
            "signsOfLife": {"heartbeat": 0, "waitingFor": "database", "since": AT}})
        self.clock = MovedClock()
        self.life = SignsOfLife(self.folder, self.clock)


class Heartbeat(LifeHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class Waiting(LifeHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class RoundsWithLife(LifeHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.

# Archived complete imports; restore needed names in their original scope, not at this file tail.
