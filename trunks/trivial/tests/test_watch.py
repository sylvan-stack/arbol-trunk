# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest import mock

from fake_driver import MovedClock
from arbol_trunk_trivial.life import SignsOfLife
from arbol_trunk_trivial.watch import Watch

import unittest


class Watching(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class EndingTheGroup(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class WatchLifetime(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class DeliberateHang(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.

# Archived complete imports; restore needed names in their original scope, not at this file tail.
