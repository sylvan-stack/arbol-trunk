# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import json
import os
import stat
import tempfile
from pathlib import Path

from arbol_trunk_trivial.request import run_request, write_request

import unittest
from typing import Any

EXCHANGE = "2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f"
CHAT = "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"
HISTORY: list[dict[str, Any]] = [
    {"type": "message", "role": "user", "text": "What does build.sh do?"},
    {"type": "message", "role": "assistant", "text": "Let me read it."},
    {"type": "tool_call", "name": "shell", "input": {"command": "cat build.sh"}, "ok": True,
     "result": {"output": "#!/bin/sh\nset -e\n…", "exitCode": 0}},
    {"type": "message", "role": "assistant", "text": "It compiles the three packages and copies them to dist/."},
]


class Request(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
