import asyncio
import unittest
from datetime import UTC, datetime
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import psycopg

from arbol_trunk_trivial.database import DatabaseUnavailable, PostgresConnection, RowRejected
from arbol_trunk_trivial.rows import MessageRow
from arbol_trunk_trivial.saver import Saver


class RejectedRows(unittest.TestCase):
    def connection(self, error: psycopg.Error) -> tuple[PostgresConnection, MagicMock, list[tuple[str, Any]]]:
        raw = MagicMock()
        cursor = raw.cursor.return_value.__aenter__.return_value
        cursor.fetchone = AsyncMock(return_value=(None,))
        calls: list[tuple[str, Any]] = []

        async def execute(sql: str, params: Any) -> None:
            calls.append((sql, params))
            if sql.startswith("INSERT INTO messages") and params[-1] == "refuse this":
                raise error

        raw.execute = AsyncMock(side_effect=execute)
        cursor.execute = AsyncMock(side_effect=execute)
        raw.close = AsyncMock()
        return PostgresConnection(raw), raw, calls

    def test_classes_22_and_23_are_permanent_and_other_failures_are_retryable(self) -> None:
        for error in (psycopg.errors.CheckViolation(), psycopg.errors.InvalidTextRepresentation(),
                      psycopg.errors.ConnectionFailure()):
            with self.subTest(sqlstate=error.sqlstate):
                connection, _raw, calls = self.connection(error)
                expected = DatabaseUnavailable if error.sqlstate == "08006" else RowRejected
                with self.assertRaises(expected):
                    asyncio.run(connection.save(MessageRow("x", 7, "refuse this")))
                self.assertEqual(len(calls), 1)

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
