# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from unittest import mock

from arbol_trunk_trivial.termination import end_group

import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "src"


class Termination(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
