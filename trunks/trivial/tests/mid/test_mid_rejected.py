"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_rejected as _support
from test_rejected import (Any ,AsyncMock ,DatabaseUnavailable ,MessageRow ,Row ,UTC ,asyncio ,datetime ,psycopg)


class RejectedRows(_support.RejectedRows):


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
