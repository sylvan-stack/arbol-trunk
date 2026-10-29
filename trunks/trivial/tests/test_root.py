# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.

from stand_ins import security_stand_in
from arbol_trunk_trivial.errors import Refusal
from arbol_trunk_trivial.root import database_address, find_root, keychain_password, role, roots_folder

import json
import tempfile
import unittest
from pathlib import Path


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")


class TheRoot(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(folder.name)


class TheDatabase(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(folder.name)


# Archived complete imports; restore needed names in their original scope, not at this file tail.
