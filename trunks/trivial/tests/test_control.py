# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""Reading `control` (RCT-1.7)."""


import os
import tempfile
import unittest
from pathlib import Path

from arbol_trunk_trivial.control import ControlFile

STOP = '{"type":"stop"}'
ANSWER = '{"type":"answer","askId":"ask_1","answer":{"type":"answers","answers":{"branch":["main"]}}}'


class Control(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "control"
        self.path.write_bytes(b"")
        self.control = ControlFile(self.path)
        self.addCleanup(self.control.close)

    def append(self, data: bytes) -> None:
        descriptor = os.open(self.path, os.O_WRONLY | os.O_APPEND)
        try:
            os.write(descriptor, data)
        finally:
            os.close(descriptor)
