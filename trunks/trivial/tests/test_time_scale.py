# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
"""Exercise the actual wait paths named by RCT-4, with a scale of ten and moved awake clocks."""


from test_life import LifeHome


class TimeScaledWaits(LifeHome):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.

# Archived complete imports; restore needed names in their original scope, not at this file tail.
