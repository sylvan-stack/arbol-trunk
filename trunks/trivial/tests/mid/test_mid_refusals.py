"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_refusals as _support
from test_refusals import (ROUTE ,security_stand_in ,time)


class TheRootTheKeychainAndTheFolder(_support.TheRootTheKeychainAndTheFolder):


# TEST-TIER-BEGIN trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_keychain_read_that_gives_no_answer_within_2_seconds_is_refused_naming_the_keychain
    def test_a_keychain_read_that_gives_no_answer_within_2_seconds_is_refused_naming_the_keychain(self) -> None:
        self.security = security_stand_in(self.home, sleep=30)
        began = time.monotonic()
        message = self.refused("database_unavailable", *ROUTE, "hi")
        self.assertLess(time.monotonic() - began, 3.0)
        self.assertIn("Keychain", message)
        self.assertIn("2 seconds", message)
        self.assertEqual(self.database.connections, 0)
# TEST-TIER-END trunks/trivial/tests/test_refusals.py::TheRootTheKeychainAndTheFolder.test_a_keychain_read_that_gives_no_answer_within_2_seconds_is_refused_naming_the_keychain
