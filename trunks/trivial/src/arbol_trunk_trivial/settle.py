"""Recover a dead Exchange from its versioned folder and recorded Build."""

from __future__ import annotations

import asyncio
import json
import os
import stat
import time
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Any

from . import CODE_NAME
from .build import Compatibility, build_info
from .claim import exchange_lock
from .clock import iso
from .database import (
    Connect,
    Connection,
    DatabaseUnavailable,
    SchemaRefusal,
    StoredExchange,
    installed_postgres,
    preflight,
)
from .end import End
from .errors import Refusal
from .folder import EXCHANGE_FORMAT, ExchangeFolder
from .output import Output
from .process import process_alive as process_alive
from .root import SECURITY, Installation, read_json
from .rows import Row, RowMaker, RunRow, moment
from .storage import stored as stored_value

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


async def open_settlement(context: Installation, exchange: str, build: str, *, connect: Connect,
                          deadline: float) -> Settlement | None:
    """Open an exact assignment and preserve the folder whenever its outcome is uncertain."""
    path = context.exchanges / exchange
    try:
        info = path.lstat()
        record_info = (path / "record.json").lstat()
        if (not stat.S_ISDIR(info.st_mode) or not stat.S_ISREG(record_info.st_mode)
                or any(item.st_uid != os.getuid() or item.st_mode & 0o077 for item in (info, record_info))):
            raise ValueError
        record = read_json(path / "record.json")
        if (not isinstance(record, dict) or record.get("exchange") != exchange
                or type(record.get("exchangeFormat")) is not int or record["exchangeFormat"] != EXCHANGE_FORMAT):
            raise ValueError
    except (OSError, ValueError):
        raise Refusal("trunk_failed", "The Exchange record cannot be verified.") from None
    if record.get("trunk") != CODE_NAME or record.get("build") != build:
        raise Refusal("no_fit", "Settlement requires the recorded Trunk Build.")
    if process_alive(record.get("process")):
        raise Refusal("alive", "The Exchange's recorded process still lives.")
    folder = ExchangeFolder(context.exchanges, exchange, record)
    connection: Connection | None = None
    keep = False
    try:
        async with asyncio.timeout(max(deadline - time.monotonic(), 0)):
            connection = await connect()
            prior = await connection.find_exchange(exchange)
            if prior is None:
                if "acceptedAt" in record or "end" in record:
                    raise Refusal("trunk_failed", "The recorded acceptance is missing from the installed database.")
                folder.remove()
                return None
            stored = await connection.exchange_state(exchange)
        if (stored is None or prior.exchange != exchange or prior.chat != record.get("chat")
                or prior.trunk != record["trunk"] or prior.build != record["build"]):
            raise Refusal("trunk_failed", "The Exchange folder differs from its saved assignment.")
        keep = True
        return Settlement(folder, connection, stored)
    except SchemaRefusal as error:
        raise error.refusal() from None
    except (DatabaseUnavailable, TimeoutError):
        raise Refusal("database_unavailable", "The database did not confirm the Exchange assignment.") from None
    except OSError:
        raise Refusal("trunk_failed", "The abandoned Exchange folder could not be removed.") from None
    finally:
        if connection is not None and not keep:
            await connection.close()


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


async def settle_exchange(context: Installation, exchange: str, *, output: Output,
                          security: str = SECURITY, connect: Connect | None = None,
                          build: str | None = None, compatibility: Compatibility | None = None) -> int:
    if build is None or compatibility is None:
        build, compatibility = build_info()
    deadline = time.monotonic() + DATABASE_SECONDS
    if connect is None:
        connect = installed_postgres(context, security, compatibility)
        await preflight(connect, deadline)
    if os.path.lexists(context.exchanges / exchange):
        async with exchange_lock(context.exchanges, deadline):
            if os.path.lexists(context.exchanges / exchange):
                state = await _settle_locked(context, exchange, build, connect=connect, deadline=deadline)
            else:
                state = await _stored_state(exchange, connect, deadline=deadline)
    else:
        state = await _stored_state(exchange, connect, deadline=deadline)
    if state == "open":
        raise Refusal("trunk_failed", "An open Exchange has no recoverable folder.")
    output.line(json.dumps({"exchange": exchange, "settled": state}, separators=(",", ":")))
    return 0


async def _stored_state(exchange: str, connect: Connect, *, deadline: float) -> str:
    connection: Connection | None = None
    try:
        async with asyncio.timeout(max(deadline - time.monotonic(), 0)):
            connection = await connect()
            stored = await connection.exchange_state(exchange)
        return stored.state if stored is not None else "none"
    except SchemaRefusal as error:
        raise error.refusal() from None
    except (DatabaseUnavailable, TimeoutError):
        raise Refusal("database_unavailable", "The database did not answer within 10 seconds.") from None
    finally:
        if connection is not None:
            await connection.close()


async def _settle_locked(context: Installation, exchange: str, build: str, *,
                         connect: Connect, deadline: float) -> str:
    pending = await open_settlement(context, exchange, build, connect=connect, deadline=deadline)
    if pending is None:
        return "none"
    try:
        path = pending.folder.path / "events.jsonl"
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError
        found = replay(path, exchange, pending.stored.accepted_at)
        end = final_end(pending.folder.record, found)
        written = bool(pending.folder.record.get("end") or found.end)
        stored = pending.stored
        if stored.state == "open":
            async with asyncio.timeout(max(deadline - time.monotonic(), 0)):
                await pending.connection.end(exchange, found.rows, end.state, end.at, end.error, end_written=written)
                confirmed = await pending.connection.exchange_state(exchange)
            if confirmed is None or confirmed.state == "open":
                raise Refusal("trunk_failed", "The database did not confirm a terminal Exchange.")
            stored = confirmed
        if written and (stored.state != end.state or stored.ended_at is None or iso(stored.ended_at) != iso(end.at)
                        or stored.error != stored_value(end.error)):
            raise Refusal("trunk_failed", "The saved terminal state differs from the Exchange folder.")
        pending.folder.remove()
        return stored.state
    except (DatabaseUnavailable, TimeoutError):
        raise Refusal("database_unavailable", "The database did not confirm settlement.") from None
    except (OSError, ValueError):
        raise Refusal("trunk_failed", "The Exchange folder could not be read or removed.") from None
    finally:
        await pending.connection.close()
