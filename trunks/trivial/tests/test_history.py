# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.

from arbol_trunk_trivial.history import HistoryRow, make_history

import unittest

from arbol_trunk_trivial.history import HistoryRow


def message(number: int, position: int, text: str, *, replaced: bool = False) -> HistoryRow:
    return HistoryRow(number, position, replaced, role="user" if position == 0 else "assistant", text=text)


class History(unittest.TestCase):

    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/test_history.py::History.test_the_first_message_of_a_chat_has_an_empty_history
# Reason: An empty input to a list projection yields an empty list; no filtering/order boundary is exercised.
# Source: arbol-trunk@a022478f6094270d20b79133b6c0d1bce70f7862:trunks/trivial/tests/test_history.py
# Retained evidence at review: Request.test_the_first_message_has_an_empty_history_and_only_what_the_route_names and whole-exchange history cases remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_first_message_of_a_chat_has_an_empty_history(self) -> None:
#         self.assertEqual(make_history([], before=1), [])
# LOW-TIER-SOURCE-END
# LOW-TIER-END
