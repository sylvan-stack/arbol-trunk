# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import json
from datetime import UTC, datetime
from typing import Any

from psycopg.types.json import Jsonb
from arbol_trunk_trivial.folder import encode
from arbol_trunk_trivial.rows import MessageRow, Row, RunRow, ToolCallRow
from arbol_trunk_trivial.storage import stored

import unittest

BAD = "A\0\ud83dB\ude00"
GOOD = "A\ufffd\ufffdB\ufffd"


class Storage(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
