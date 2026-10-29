"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_rejected as _support
from test_rejected import (
    Any,
    AsyncMock,
    DatabaseUnavailable,
    MagicMock,
    MessageRow,
    PostgresConnection,
    RejectedRows,
    Row,
    RowRejected,
    Saver,
    UTC,
    asyncio,
    cast,
    datetime,
    psycopg,
    unittest,
)


class RejectedRows(_support.RejectedRows):
# TEST-TIER-BEGIN trunks/trivial/tests/test_rejected.py::RejectedRows.test_classes_22_and_23_are_permanent_and_other_failures_are_retryable
    def test_classes_22_and_23_are_permanent_and_other_failures_are_retryable(self) -> None:
        for error in (psycopg.errors.CheckViolation(), psycopg.errors.InvalidTextRepresentation(),
                      psycopg.errors.ConnectionFailure()):
            with self.subTest(sqlstate=error.sqlstate):
                connection, _raw, calls = self.connection(error)
                expected = DatabaseUnavailable if error.sqlstate == "08006" else RowRejected
                with self.assertRaises(expected):
                    asyncio.run(connection.save(MessageRow("x", 7, "refuse this")))
                self.assertEqual(len(calls), 1)
# TEST-TIER-END trunks/trivial/tests/test_rejected.py::RejectedRows.test_classes_22_and_23_are_permanent_and_other_failures_are_retryable

# TEST-TIER-BEGIN trunks/trivial/tests/test_rejected.py::RejectedRows.test_a_refused_row_is_skipped_without_retry_and_following_rows_are_saved
    def test_a_refused_row_is_skipped_without_retry_and_following_rows_are_saved(self) -> None:
        connection, _raw, calls = self.connection(psycopg.errors.CheckViolation())

        async def work() -> Saver:
            async def connect() -> PostgresConnection:
                return connection
            saver = Saver(connect)
            saver.add([MessageRow("x", 7, "refuse this"), MessageRow("x", 8, "keep this")])
            saver.start()
            for _ in range(100):
                await asyncio.sleep(0)
                if saver.saved == 2:
                    break
            await saver.stop()
            return saver

        saver = asyncio.run(work())
        self.assertEqual([params[-1] for _sql, params in calls], ["refuse this", "keep this"])
        self.assertEqual(saver.unsaved, [])
        self.assertEqual(cast(RowRejected, saver.rejected).line, 7)
        self.assertEqual(saver.failures, 0)
# TEST-TIER-END trunks/trivial/tests/test_rejected.py::RejectedRows.test_a_refused_row_is_skipped_without_retry_and_following_rows_are_saved

# TEST-TIER-BEGIN trunks/trivial/tests/test_rejected.py::RejectedRows.test_a_row_already_refused_is_not_retried_when_the_outer_commit_loses_the_server
    def test_a_row_already_refused_is_not_retried_when_the_outer_commit_loses_the_server(self) -> None:
        connection, raw, calls = self.connection(psycopg.errors.CheckViolation())
        exits = 0

        async def exit_transaction(*args: Any) -> bool:
            nonlocal exits
            exits += 1
            if exits == 3:
                raise psycopg.errors.ConnectionFailure("Lost at the outer commit.")
            return False

        raw.transaction.return_value.__aexit__ = AsyncMock(side_effect=exit_transaction)
        rows: list[Row] = [MessageRow("x", 7, "refuse this"), MessageRow("x", 8, "keep")]
        with self.assertRaises(DatabaseUnavailable):
            asyncio.run(connection.end("x", rows, "completed", datetime.now(UTC), None))
        self.assertEqual(rows, [MessageRow("x", 8, "keep")])
        again, _raw, later = self.connection(psycopg.errors.CheckViolation())
        asyncio.run(again.end("x", rows, "completed", datetime.now(UTC), None))
        self.assertEqual([params[-1] for sql, params in calls + later if sql.startswith("INSERT INTO messages")],
                         ["refuse this", "keep", "keep"])
# TEST-TIER-END trunks/trivial/tests/test_rejected.py::RejectedRows.test_a_row_already_refused_is_not_retried_when_the_outer_commit_loses_the_server

# TEST-TIER-BEGIN trunks/trivial/tests/test_rejected.py::RejectedRows.test_final_saving_uses_a_savepoint_and_preserves_an_already_written_end
    def test_final_saving_uses_a_savepoint_and_preserves_an_already_written_end(self) -> None:
        for end_written in (False, True):
            with self.subTest(end_written=end_written):
                connection, raw, calls = self.connection(psycopg.errors.CheckViolation())
                asyncio.run(connection.end("x", [MessageRow("x", 7, "refuse this"), MessageRow("x", 8, "keep")],
                                           "interrupted", datetime.now(UTC), None, end_written=end_written))
                self.assertEqual(raw.transaction.call_count, 3)  # outer atomic end, then a savepoint for each row
                update = calls[-1][1]
                self.assertEqual(update[0], "interrupted" if end_written else "failed")
                if not end_written:
                    self.assertEqual(update[2].obj["code"], "trunk_failed")
                    self.assertIn("line 7", update[2].obj["message"])
                self.assertEqual(len([sql for sql, _ in calls if sql.startswith("INSERT INTO messages")]), 2)
# TEST-TIER-END trunks/trivial/tests/test_rejected.py::RejectedRows.test_final_saving_uses_a_savepoint_and_preserves_an_already_written_end
