# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.

from arbol_trunk_trivial.history import HistoryRow, make_history

import unittest

from arbol_trunk_trivial.history import HistoryRow


def message(number: int, position: int, text: str, *, replaced: bool = False) -> HistoryRow:
    return HistoryRow(number, position, replaced, role="user" if position == 0 else "assistant", text=text)


class History(unittest.TestCase):

    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
