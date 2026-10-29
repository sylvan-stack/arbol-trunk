# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import os

from arbol_trunk_trivial.driver import Line, as_event

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from arbol_trunk_trivial.driver import Line
from arbol_trunk_trivial.events import EventsFile

EVENTS = [
    b'{"runId":"x.1","seq":1,"at":"2026-10-15T09:30:01.204Z","type":"started","continuity":"fresh"}',
    b'{"runId":"x.1","seq":2,"type":"text_delta","text":"Let me "}',
    b'{"type": "text", "runId": "x.1", "seq": 3, "text": "Let me read it. \\ud83d"}',
]


class Events(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "events.jsonl"
        self.path.write_bytes(b"")
        self.file = EventsFile(self.path)
        self.addCleanup(self.file.close)


# Archived complete imports; restore needed names in their original scope, not at this file tail.
