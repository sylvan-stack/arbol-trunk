import asyncio
import time
import unittest
from collections.abc import Callable, Sequence
from unittest import mock

from fakes import FakeDatabase

from arbol_trunk_trivial import saver
from arbol_trunk_trivial.rows import MessageRow, Row
from arbol_trunk_trivial.saver import Saver

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
    def test_rows_are_saved_one_at_a_time_and_in_order(self) -> None:
        database = FakeDatabase()

        async def go() -> None:
            keeper = Saver(database.connect())
            keeper.start()
            keeper.add(rows(3, 4))
            keeper.add(rows(6))
            await until(lambda: keeper.saved == 3)
            await keeper.stop()

        asyncio.run(go())
        self.assertEqual([row.position for row in database.saves], [3, 4, 6])  # type: ignore[union-attr]
        self.assertEqual(database.connections, 1)

    def test_the_loop_never_waits_for_a_slow_database(self) -> None:
        database = FakeDatabase(delay=0.5)

        async def go() -> list[float]:
            keeper = Saver(database.connect())
            keeper.start()
            rounds = []
            for position in range(1, 6):
                began = time.monotonic()
                keeper.add(rows(position))
                await asyncio.sleep(0.01)
                rounds.append(time.monotonic() - began)
            await keeper.stop()
            return rounds

        self.assertLess(max(asyncio.run(go())), 0.2)

    def test_a_failed_call_is_given_up_with_its_connection_and_tried_again_later_on_a_new_one(self) -> None:
        database = FakeDatabase(fail_save=2)

        async def go() -> Saver:
            keeper = Saver(database.connect())
            keeper.start()
            keeper.add(rows(3, 4))
            await until(lambda: keeper.saved == 2)
            await keeper.stop()
            return keeper

        with mock.patch.object(saver, "RETRY_SECONDS", 0.05):
            keeper = asyncio.run(go())
        self.assertEqual((keeper.saved, keeper.failures), (2, 2))
        self.assertEqual([row.position for row in database.saves], [3, 4])  # type: ignore[union-attr]
        self.assertEqual(database.connections, 3)
        self.assertEqual(database.closed, 2)

    def test_the_wait_between_tries_is_divided_by_the_time_scale(self) -> None:
        database = FakeDatabase(fail_save=1)

        async def go() -> float:
            keeper = Saver(database.connect())
            keeper.start()
            began = time.monotonic()
            keeper.add(rows(3))
            await until(lambda: keeper.saved == 1, 10)
            await keeper.stop()
            return time.monotonic() - began

        with mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "50"}):
            took = asyncio.run(go())
        self.assertGreaterEqual(took, 0.09)
        self.assertLess(took, 1.0)

    def test_what_is_not_saved_when_it_stops_stays_for_the_end(self) -> None:
        database = FakeDatabase(fail_connect=100)

        async def go() -> Saver:
            keeper = Saver(database.connect())
            keeper.start()
            keeper.add(rows(3, 4))
            await asyncio.sleep(0.05)
            await keeper.stop()
            return keeper

        keeper = asyncio.run(go())
        self.assertEqual([row.position for row in keeper.unsaved], [3, 4])  # type: ignore[union-attr]


if __name__ == "__main__":
    unittest.main()
