# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""Exercise the actual wait paths named by RCT-4, with a scale of ten and moved awake clocks."""
import asyncio
import signal
from unittest import mock

from fake_driver import MovedClock, ScriptedDriver, finished
from fakes import FakeDatabase
from arbol_trunk_trivial.end import End, save_end
from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.life import SignsOfLife
from arbol_trunk_trivial.rows import MessageRow, RowMaker
from arbol_trunk_trivial.run import drive
from arbol_trunk_trivial.saver import Saver
from arbol_trunk_trivial.termination import end_group
from arbol_trunk_trivial.watch import Watch


from test_life import LifeHome


class TimeScaledWaits(LifeHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.

# Archived complete imports; restore needed names in their original scope, not at this file tail.
