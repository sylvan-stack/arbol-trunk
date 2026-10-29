# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from package_fixtures import package_source

from scripts.package_build import package


class PackageChecks(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.source, cache = package_source(self.base)
        self.folder = self.base / "build"
        self.folder.mkdir()
        with mock.patch.dict("os.environ", {"ARBOL_PYTHON_ARCHIVE_CACHE": str(cache)}):
            package(str(self.folder), root=self.source)


# Archived complete imports; restore needed names in their original scope, not at this file tail.
