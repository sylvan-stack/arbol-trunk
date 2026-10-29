# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
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
