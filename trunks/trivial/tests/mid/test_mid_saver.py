"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_saver as _support
from test_saver import (
    Callable,
    FakeConnection,
    FakeDatabase,
    MessageRow,
    MovedClock,
    Row,
    Saver,
    Saving,
    Sequence,
    X,
    asyncio,
    mock,
    positions,
    rows,
    saver,
    time,
    unittest,
    until,
)


class Saving(_support.Saving):
# TEST-TIER-BEGIN trunks/trivial/tests/test_saver.py::Saving.test_rows_are_saved_one_at_a_time_and_in_order
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
        self.assertEqual(positions(database.saves), [3, 4, 6])
        self.assertEqual(database.connections, 1)
# TEST-TIER-END trunks/trivial/tests/test_saver.py::Saving.test_rows_are_saved_one_at_a_time_and_in_order

# TEST-TIER-BEGIN trunks/trivial/tests/test_saver.py::Saving.test_the_loop_never_waits_for_a_slow_database
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
# TEST-TIER-END trunks/trivial/tests/test_saver.py::Saving.test_the_loop_never_waits_for_a_slow_database

# TEST-TIER-BEGIN trunks/trivial/tests/test_saver.py::Saving.test_a_failed_call_is_given_up_with_its_connection_and_tried_again_later_on_a_new_one
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
        self.assertEqual(positions(database.saves), [3, 4])
        self.assertEqual(database.connections, 3)
        self.assertEqual(database.closed, 2)
# TEST-TIER-END trunks/trivial/tests/test_saver.py::Saving.test_a_failed_call_is_given_up_with_its_connection_and_tried_again_later_on_a_new_one

# TEST-TIER-BEGIN trunks/trivial/tests/test_saver.py::Saving.test_the_wait_between_tries_is_divided_by_the_time_scale
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
# TEST-TIER-END trunks/trivial/tests/test_saver.py::Saving.test_the_wait_between_tries_is_divided_by_the_time_scale

# TEST-TIER-BEGIN trunks/trivial/tests/test_saver.py::Saving.test_retries_wait_five_scaled_seconds_on_new_connections_and_keep_row_order
    def test_retries_wait_five_scaled_seconds_on_new_connections_and_keep_row_order(self) -> None:
        clock = MovedClock()
        database = FakeDatabase(fail_save=2)
        sleep = asyncio.sleep
        waits: list[float] = []
        attempts: list[tuple[float, int, int]] = []
        save = FakeConnection.save

        async def advance(seconds: float) -> None:
            waits.append(seconds)
            clock.t += seconds
            await sleep(0)

        async def record(connection: FakeConnection, row: Row) -> None:
            assert isinstance(row, MessageRow)
            attempts.append((clock.since_start(), database.connections, row.position))
            await save(connection, row)

        async def work() -> None:
            keeper = Saver(database.connect())
            keeper.add(rows(3, 4))
            keeper.start()
            for _ in range(100):
                await sleep(0)
                if keeper.saved == 2:
                    break
            await keeper.stop()
            self.assertEqual(keeper.saved, 2)

        with mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "10"}), \
                mock.patch("arbol_trunk_trivial.saver.asyncio.sleep", advance), \
                mock.patch.object(FakeConnection, "save", record):
            asyncio.run(work())
        self.assertEqual(waits, [0.5, 0.5])
        self.assertEqual(attempts, [(0, 1, 3), (0.5, 2, 3), (1, 3, 3), (1, 3, 4)])
        self.assertEqual(database.closed, 2)
# TEST-TIER-END trunks/trivial/tests/test_saver.py::Saving.test_retries_wait_five_scaled_seconds_on_new_connections_and_keep_row_order

# TEST-TIER-BEGIN trunks/trivial/tests/test_saver.py::Saving.test_what_is_not_saved_when_it_stops_stays_for_the_end
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
        self.assertEqual(positions(keeper.unsaved), [3, 4])
# TEST-TIER-END trunks/trivial/tests/test_saver.py::Saving.test_what_is_not_saved_when_it_stops_stays_for_the_end
