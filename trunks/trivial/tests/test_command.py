# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import json
import os
import tempfile
import unittest
from pathlib import Path

EXCHANGE = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"


class CommandLine(unittest.TestCase):


    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class RequestFile(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.work = os.path.realpath(self.folder.name)

    def request(self, value: object) -> str:
        file = Path(self.work) / "start.json"
        file.write_text(json.dumps(value), encoding="utf-8")
        return str(file)



# Archived complete imports; restore needed names in their original scope, not at this file tail.
