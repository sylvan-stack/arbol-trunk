"""Save an Exchange whose process is gone, using its folder and the Root Contract alone (RCT-2.12)."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Any

from .claim import root_lock
from .database import Connect, Connection, DatabaseUnavailable, StoredExchange, conninfo, postgres
from .end import End
from .errors import Refusal
from .folder import ExchangeFolder
from .output import Output
from .process import process_alive as process_alive
from .root import SECURITY, database_address, find_root, keychain_password, read_json, role
from .rows import Row, RowMaker, RunRow, moment

DATABASE_SECONDS = 10.0  # not divided by ARBOL_TEST_TIME_SCALE (RCT-4)


@dataclass
class Settlement:
    folder: ExchangeFolder
    connection: Connection
    stored: StoredExchange


@dataclass
class Replay:
    rows: list[Row]
    end: dict[str, Any] | None
    last_at: datetime


def replay(path: Path, exchange: str, accepted_at: datetime) -> Replay:
    """Read only whole lines. Live saving and recovery share RowMaker, including unanswered questions and open
    calls; small-call finished events use the same run-row rules with kind small."""
    maker = RowMaker(exchange)
    rows: list[Row] = []
    end: dict[str, Any] | None = None
    last_at = accepted_at
    with path.open("rb") as stream:
        for raw in stream:
            if not raw.endswith(b"\n"):
                break
            try:
                line = json.loads(raw.decode("utf-8", "surrogatepass"))
            except (UnicodeError, ValueError):
                continue
            if not isinstance(line, dict):
                continue
            event = line.get("event")
            small = line.get("smallRun")
            if isinstance(event, dict) and isinstance(event.get("runId"), str):
                n = line.get("n")
                if isinstance(n, int) and not isinstance(n, bool) and n > 0:
                    rows.extend(maker.take(n, event))
            elif isinstance(small, dict) and small.get("type") == "finished":
                rows.extend(replace(row, kind="small", started=None)
                            for row in RowMaker(exchange).take(line["n"] if type(line.get("n")) is int else 0, small)
                            if isinstance(row, RunRow))
            elif isinstance(line.get("answer"), dict):
                maker.take_answer(line["answer"])
            elif isinstance(line.get("end"), dict):
                end = line["end"]
            carried = event if isinstance(event, dict) else small
            if isinstance(carried, dict) and isinstance(carried.get("at"), str):
                try:
                    last_at = datetime.fromisoformat(carried["at"])
                except ValueError:
                    pass
    for run_id in maker.seen:
        maker.last_at.setdefault(run_id, accepted_at.isoformat())
    rows.extend(maker.at_end())
    return Replay(rows, end, moment(last_at.isoformat()))


async def open_settlement(home: Path, root_id: str, exchange: str, *, security: str = SECURITY,
                          connect: Connect | None = None, deadline: float | None = None) -> Settlement | None:
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
        deadline = deadline if deadline is not None else time.monotonic() + DATABASE_SECONDS
        async with asyncio.timeout(max(deadline - time.monotonic(), 0)):
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


def final_end(record: dict[str, Any], found: Replay) -> End:
    value = record.get("end") or found.end
    if value is None:
        return End("interrupted", found.last_at)
    if not isinstance(value, dict) or value.get("state") not in ("completed", "failed", "cancelled"):
        raise Refusal("trunk_failed", "The Exchange record holds no readable end.")
    try:
        at = datetime.fromisoformat(value["at"])
        if at.tzinfo is None:
            raise ValueError("An end needs an absolute time.")
    except (KeyError, TypeError, ValueError):
        raise Refusal("trunk_failed", "The Exchange end holds no readable time.") from None
    error = value.get("error") if value["state"] == "failed" else None
    if value["state"] == "failed" and not isinstance(error, dict):
        raise Refusal("trunk_failed", "The failed Exchange end holds no error.")
    return End(value["state"], at, error)


async def settle_exchange(home: Path, root_id: str, exchange: str, *, output: Output,
                          security: str = SECURITY, connect: Connect | None = None) -> int:
    state = "none"
    root = find_root(home, root_id)
    if (root.exchanges / exchange).exists():
        deadline = time.monotonic() + DATABASE_SECONDS
        async with root_lock(root.exchanges, deadline):
            if (root.exchanges / exchange).exists():
                state = await _settle_locked(home, root_id, exchange, security=security, connect=connect,
                                             deadline=deadline)
            else:
                # The folder existed before we waited: another settler removed it, so report its stored result.
                state = await _stored_state(home, root_id, exchange, security=security, connect=connect,
                                            deadline=deadline)
    output.line(json.dumps({"exchange": exchange, "settled": state}, separators=(",", ":")))
    return 0


async def _stored_state(home: Path, root_id: str, exchange: str, *, security: str,
                        connect: Connect | None, deadline: float) -> str:
    connection: Connection | None = None
    try:
        if connect is None:
            root = find_root(home, root_id)
            address = database_address(home)
            connect = postgres(conninfo(address, root.database, keychain_password(role(address), security)))
        async with asyncio.timeout(max(deadline - time.monotonic(), 0)):
            connection = await connect()
            stored = await connection.exchange_state(exchange)
        return stored.state if stored is not None else "none"
    except (DatabaseUnavailable, TimeoutError):
        raise Refusal("database_unavailable", "The database did not answer within 10 seconds.") from None
    finally:
        if connection is not None:
            await connection.close()


async def _settle_locked(home: Path, root_id: str, exchange: str, *, security: str,
                         connect: Connect | None, deadline: float) -> str:
    pending = await open_settlement(home, root_id, exchange, security=security, connect=connect, deadline=deadline)
    state = "none"
    if pending is not None:
        try:
            found = replay(pending.folder.path / "events.jsonl", exchange, pending.stored.accepted_at)
            end = final_end(pending.folder.record, found)
            async with asyncio.timeout(max(deadline - time.monotonic(), 0)):
                await pending.connection.end(exchange, found.rows, end.state, end.at, end.error,
                                             end_written=bool(pending.folder.record.get("end") or found.end))
                stored = await pending.connection.exchange_state(exchange)
            state = stored.state if stored is not None else "none"
            pending.folder.remove()
        except (DatabaseUnavailable, TimeoutError):
            raise Refusal("database_unavailable", "The database did not take the saved Exchange within 10 seconds.") from None
        except (OSError, ValueError):
            raise Refusal("trunk_failed", "The Exchange folder could not be read or removed.") from None
        finally:
            await pending.connection.close()
    return state
