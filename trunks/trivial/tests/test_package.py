# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from package_fixtures import package_source


class Packaging(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.source, self.cache = package_source(self.base)
        self.output = self.base / "package"
        self.output.mkdir()
        patch = mock.patch.dict("os.environ", {"ARBOL_PYTHON_ARCHIVE_CACHE": str(self.cache)})
        patch.start()
        self.addCleanup(patch.stop)


# Archived complete imports; restore needed names in their original scope, not at this file tail.
