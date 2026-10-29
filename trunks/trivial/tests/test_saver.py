# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import asyncio
import time
import unittest
from collections.abc import Callable, Sequence

from arbol_trunk_trivial.rows import MessageRow, Row

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"


def rows(*positions: int) -> list[MessageRow]:
    return [MessageRow(X, position, f"block {position}") for position in positions]


def positions(saved: Sequence[Row]) -> list[int]:
    return [row.position for row in saved if isinstance(row, MessageRow)]


async def until(condition: Callable[[], bool], seconds: float = 5) -> None:
    deadline = time.monotonic() + seconds
    while not condition() and time.monotonic() < deadline:
        await asyncio.sleep(0.01)


class Saving(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.



# Archived complete imports; restore needed names in their original scope, not at this file tail.
