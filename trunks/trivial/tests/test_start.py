# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.

from audit import opened_files
from arbol_trunk_trivial.settings import default_driver, settings_file

import json
import os
import tempfile
import unittest
from pathlib import Path

from stand_ins import security_stand_in

from arbol_trunk_trivial.command import handed, parse
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.start import Prepared, prepare


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")


class Start(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(os.path.realpath(folder.name))
        write(roots_folder(self.home) / "rct" / "root.json", {"database": "arbol_rct", "rootContract": 1})
        write(self.home / ".arbol" / "database.json", {"address": "postgresql://rct@%2Ftmp%2Frct-1a2b"})
        self.security = str(security_stand_in(self.home, status=44))

    def start(self, *args: str) -> Prepared:
        return prepare(handed(parse(["--root", "rct", "run", *args, "hi"]), started_in=str(self.home)), self.home,
                       self.security)


# Archived complete imports; restore needed names in their original scope, not at this file tail.
