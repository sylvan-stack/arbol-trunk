# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import json
import time
from datetime import UTC, datetime

from arbol_trunk_trivial.errors import Refusal
from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.process import started_at

import os
import stat
import tempfile
import unittest
from pathlib import Path

EXCHANGE = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
RECORD = {"rootContract": 1, "root": "rct", "exchange": EXCHANGE, "chat": "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b",
          "trunk": "trivial", "build": "0", "process": {"pid": 1, "startedAt": "2026-10-15T09:30:00.000Z"},
          "route": {}, "workingFolder": "/tmp",
          "signsOfLife": {"heartbeat": 0, "waitingFor": "database", "since": "2026-10-15T09:30:00.000Z"}}


def mode(path: Path) -> int:
    return stat.S_IMODE(os.stat(path).st_mode)


class Folder(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.exchanges = Path(folder.name)
        os.umask(0o022)


class Process(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
