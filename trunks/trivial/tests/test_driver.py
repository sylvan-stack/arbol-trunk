# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import asyncio
import json

from arbol_trunk_trivial.driver import DriverRun, as_event, find_launcher

import os
import tempfile
import unittest
from pathlib import Path

LONG = "x" * (300 * 1024)
LAUNCHER = """#!/bin/sh
printf '%s\\n' "$0" "$@" > "$(dirname "$0")/arguments"
printf '%s %s\\n' "$(ps -o pgid= -p $$)" "$(pwd -P)" > "$(dirname "$0")/group"
printf '%s\\n' '{{"runId":"x.1","seq":1,"type":"started"}}'
printf '%s\\n' 'not an event'
printf '%s\\n' '{{"no":"type"}}'
printf '%s\\n' '{{"runId":"x.1","seq":2,"type":"text","text":"{long}"}}'
cat > "$(dirname "$0")/control"
printf '%s' '{{"runId":"x.1","seq":3,"type":"finished","outcome":"completed"}}'
"""


def launcher(folder: Path, name: str = "arbol-claude-driver") -> Path:
    file = folder / name
    file.write_text(LAUNCHER.format(long=LONG), encoding="utf-8")
    os.chmod(file, 0o755)
    return file


class Launcher(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(os.path.realpath(folder.name))


class Run(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
