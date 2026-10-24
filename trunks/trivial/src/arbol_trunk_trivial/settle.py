"""Save an Exchange whose process is gone, using its folder and the Root Contract alone (RCT-2.12)."""

from __future__ import annotations

import asyncio
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .database import Connect, Connection, DatabaseUnavailable, StoredExchange, conninfo, postgres
from .errors import Refusal
from .folder import ExchangeFolder
from .process import started_at
from .root import SECURITY, database_address, find_root, keychain_password, read_json, role

DATABASE_SECONDS = 10.0  # not divided by ARBOL_TEST_TIME_SCALE (RCT-4)


def process_alive(process: Any) -> bool:
    """The PID must still have the recorded start time, give or take two seconds (RCT-1)."""
    if not isinstance(process, dict) or not isinstance(process.get("pid"), int) or isinstance(process["pid"], bool):
        raise Refusal("trunk_failed", "The Exchange record names no process.")
    try:
        recorded = datetime.fromisoformat(process["startedAt"])
        if recorded.tzinfo is None or process["pid"] <= 0:
            raise ValueError("A process needs a positive PID and an absolute start time.")
    except (KeyError, TypeError, ValueError):
        raise Refusal("trunk_failed", "The Exchange record names no readable process start time.") from None
    try:
        actual = datetime.fromisoformat(started_at(process["pid"]))
    except subprocess.CalledProcessError:
        return False
    return abs((actual - recorded).total_seconds()) <= 2


@dataclass
class Settlement:
    folder: ExchangeFolder
    connection: Connection
    stored: StoredExchange


async def open_settlement(home: Path, root_id: str, exchange: str, *, security: str = SECURITY,
                          connect: Connect | None = None) -> Settlement | None:
    """No folder or never accepted: remove what remains and return None. A living process or an unavailable
    database is refused with its folder intact. Otherwise return the folder and the connection for replay."""
    root = find_root(home, root_id)
    path = root.exchanges / exchange
    if not path.exists():
        return None
    try:
        record = read_json(path / "record.json")
        if not isinstance(record, dict):
            raise ValueError("The record is no object.")
    except (OSError, ValueError):
        raise Refusal("trunk_failed", "The Exchange record cannot be read.") from None
    if process_alive(record.get("process")):
        raise Refusal("alive", "The Exchange's recorded process still lives.")
    folder = ExchangeFolder(root.exchanges, exchange, record)
    connection: Connection | None = None
    try:
        if connect is None:
            address = database_address(home)
            connect = postgres(conninfo(address, root.database, keychain_password(role(address), security)))
        async with asyncio.timeout(DATABASE_SECONDS):
            connection = await connect()
            stored = await connection.exchange_state(exchange)
        if stored is None:
            folder.remove()
            await connection.close()
            return None
        return Settlement(folder, connection, stored)
    except (DatabaseUnavailable, TimeoutError):
        if connection is not None:
            await connection.close()
        raise Refusal("database_unavailable", "The database did not answer within 10 seconds.") from None
