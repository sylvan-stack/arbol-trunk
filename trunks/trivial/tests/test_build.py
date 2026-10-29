# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import unittest
from pathlib import Path

TRUNK = Path(__file__).resolve().parents[1]


class BuildNumber(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class CheckoutScript(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.



# Archived complete imports; restore needed names in their original scope, not at this file tail.
