# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import json
import os
import shutil
import subprocess
import tempfile

from arbol_trunk_trivial import NAME
from arbol_trunk_trivial.build import BuildRecordError, build_number

import unittest
from pathlib import Path

TRUNK = Path(__file__).resolve().parents[1]


class BuildNumber(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class CheckoutScript(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
