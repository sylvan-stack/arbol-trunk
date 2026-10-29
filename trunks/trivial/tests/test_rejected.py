# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import unittest
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import psycopg

from arbol_trunk_trivial.database import PostgresConnection


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


# Archived complete imports; restore needed names in their original scope, not at this file tail.
