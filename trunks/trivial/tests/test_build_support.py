# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import json
from unittest import mock

from scripts.build_support import COMPONENT, ENTRY, ROOT, build_folder, metadata, target

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.build_support import ROOT


class BuildMetadata(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.source = Path(temporary.name).resolve() / "trunks/trivial"
        (self.source / "scripts").mkdir(parents=True)
        for name in ("pyproject.toml", "package.json", "uv.lock", ".python-version", "scripts/python-distribution.json"):
            shutil.copy2(ROOT / name, self.source / name)
        self.folder = Path(temporary.name).resolve() / "build"
        self.folder.mkdir()


# Archived complete imports; restore needed names in their original scope, not at this file tail.
