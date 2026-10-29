# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import json
import subprocess
from types import SimpleNamespace

from scripts.check_build import driver_bridge, live

import contextlib
import io
import os
import shlex
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class LiveCheck(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.owner = self.base / "owner's home"
        self.driver = self.owner / ".local/bin/arbol-claude-driver"
        self.driver.parent.mkdir(parents=True)
        self.report = self.base / "driver-arguments"
        self.driver.write_text("#!/bin/sh\nprintf '%s\\n' \"$HOME\" \"$PATH\" \"$@\" > "
                               + shlex.quote(str(self.report))
                               + "\nprintf '%s\\n' '{\"error\":{\"code\":\"not_signed_in\"}}'\nexit 1\n")
        self.driver.chmod(0o755)
        self.fixture = mock.MagicMock()
        self.fixture.home = self.base / "temporary-home"
        self.fixture.standin = self.fixture.home / "standin"
        (self.fixture.standin / "bin").mkdir(parents=True)
        self.output = io.StringIO()
        self.factory = self.enterContext(mock.patch("scripts.check_build.live_fixture", return_value=self.fixture))
        self.enterContext(contextlib.redirect_stdout(self.output))
        self.state = self.base / "empty test state"
        self.state.mkdir()
        self.enterContext(mock.patch.dict(os.environ, {"ARBOL_BUILD_TEST_STATE_DIR": str(self.state)}))


# Archived complete imports; restore needed names in their original scope, not at this file tail.
