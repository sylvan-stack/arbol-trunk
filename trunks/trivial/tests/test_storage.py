# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import unittest

BAD = "A\0\ud83dB\ude00"
GOOD = "A\ufffd\ufffdB\ufffd"


class Storage(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
