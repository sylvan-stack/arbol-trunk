# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import json
import os
import signal
import tempfile
import time
from pathlib import Path
from unittest import mock

from arbol_trunk_trivial.driver import as_event
from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.output import Output

import unittest


class ForegroundOutput(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
