"""Accepting a message (RCT-2, "Accepting a message").

The folder is made first, with a record that has no `acceptedAt`; then one transaction writes the chat, the open
Exchange and the message, and reads the history. All the work with the database for the acceptance ends within 10
seconds of the start, or the message is refused with `database_unavailable`; a busy chat is refused with `chat_busy`.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from . import CODE_NAME
from .claim import claim_folder
from .clock import iso
from .database import (
    Acceptance,
    Accepted,
    ChatBusy,
    Connect,
    Connection,
    DatabaseUnavailable,
    DuplicateExchange,
    PriorExchange,
    Replacement,
    ReplacementRefused,
)
from .errors import Refusal, invalid
from .folder import ExchangeFolder
from .history import make_history
from .start import Prepared

ACCEPTANCE_SECONDS = 10.0  # from the start; not divided by ARBOL_TEST_TIME_SCALE (RCT-4)


class Repeated(Exception):
    """An already-accepted identifier: return its acceptance and start no work."""

    def __init__(self, root: str, prior: PriorExchange) -> None:
        self.line = acceptance_line(root=root, exchange=prior.exchange, chat=prior.chat, number=prior.number,
                                    build=prior.build, trunk=prior.trunk, duplicate=True)


async def find_prior(connect: Connect, exchange: str, deadline: float) -> PriorExchange | None:
    connection: Connection | None = None

    async def work() -> PriorExchange | None:
        nonlocal connection
        connection = await connect()
        return await connection.find_exchange(exchange)

    try:
        return await asyncio.wait_for(work(), max(deadline - time.monotonic(), 0))
    except (DatabaseUnavailable, TimeoutError):
        raise Refusal("database_unavailable", "The database did not finish the identifier lookup within 10 seconds.") from None
    finally:
        await _close(connection)


async def accept_in_database(connect: Connect, acceptance: Acceptance,
                             deadline: float) -> tuple[Connection, Accepted]:
    """Connects and runs the acceptance's transaction before `deadline` (time.monotonic()); the connection stays
    open for saving the answer."""
    connection: Connection | None = None

    async def work() -> tuple[Connection, Accepted]:
        nonlocal connection
        connection = await connect()
        return connection, await connection.accept(acceptance)

    try:
        return await asyncio.wait_for(work(), max(deadline - time.monotonic(), 0))
    except ChatBusy as busy:
        await _close(connection)
        open_one = f": {busy.open_exchange}" if busy.open_exchange else ""
        raise Refusal("chat_busy", f"The chat has an Exchange in progress{open_one}.") from None
    except DuplicateExchange:
        await _close(connection)
        raise
    except ReplacementRefused as error:
        await _close(connection)
        raise Refusal(error.code, str(error)) from None
    except TimeoutError:
        await _close(connection)
        raise Refusal("database_unavailable", f"The database did not accept the message within "
                                              f"{ACCEPTANCE_SECONDS:g} seconds of the start.") from None
    except DatabaseUnavailable as error:
        await _close(connection)
        raise Refusal("database_unavailable", f"The database cannot be reached: {error}") from None


async def _close(connection: Connection | None) -> None:
    if connection is not None:
        await connection.close()


async def find_replacement(connect: Connect, exchange: str, deadline: float) -> Replacement:
    connection: Connection | None = None

    async def work() -> Replacement:
        nonlocal connection
        connection = await connect()
        return await connection.replacement(exchange)

    try:
        return await asyncio.wait_for(work(), max(deadline - time.monotonic(), 0))
    except ReplacementRefused as error:
        raise Refusal(error.code, str(error)) from None
    except (DatabaseUnavailable, TimeoutError):
        raise Refusal("database_unavailable", "The database did not finish the replacement lookup within 10 seconds.") from None
    finally:
        await _close(connection)


def acceptance_line(*, root: str, exchange: str, chat: str, number: int, build: str, duplicate: bool = False,
                     trunk: str = CODE_NAME) -> str:
    """The one line that says the message was accepted (RCT-2, Accepted)."""
    return json.dumps({"accepted": True, "duplicate": duplicate, "root": root, "exchange": exchange, "chat": chat,
                       "number": number, "trunk": trunk, "build": build}, separators=(",", ":"))


@dataclass
class Exchange:
    """An accepted Exchange: its folder, the connection the acceptance used, its number and the history it sends."""

    folder: ExchangeFolder
    connection: Connection
    chat: str
    number: int
    message: str
    history: list[dict[str, Any]]
    line: str


async def accept_message(prepared: Prepared, connect: Connect, *, build: str, process: dict[str, Any],
                         started: float) -> Exchange:
    """Steps 3 to 5 of RCT-2's acceptance: the folder with a record without `acceptedAt`, the transaction, then
    `acceptedAt`. `started` is the start of the Trunk (time.monotonic()); a refusal leaves no folder behind."""
    handed = prepared.handed
    if handed.exchange is not None:
        prior = await find_prior(connect, handed.exchange, started + ACCEPTANCE_SECONDS)
        if prior is not None:
            raise Repeated(prepared.root.identifier, prior)
    if handed.replaces is not None:
        try:
            replacement = await find_replacement(connect, handed.replaces, started + ACCEPTANCE_SECONDS)
        except Refusal:
            if handed.exchange is not None:
                prior = await find_prior(connect, handed.exchange, started + ACCEPTANCE_SECONDS)
                if prior is not None:
                    raise Repeated(prepared.root.identifier, prior) from None
            raise
        if handed.chat is not None and handed.chat != replacement.chat:
            raise invalid("The handed chat differs from the replaced Exchange's chat.")
        chat, message = replacement.chat, replacement.message
    else:
        chat = handed.chat or str(uuid.uuid4())
        assert handed.message is not None  # handed() refuses a missing message
        message = handed.message
    exchange = handed.exchange or str(uuid.uuid4())
    record: dict[str, Any] = {"rootContract": prepared.root.root_contract, "root": prepared.root.identifier,
                              "exchange": exchange, "chat": chat, "trunk": CODE_NAME, "build": build,
                              "process": process, "route": handed.route}
    if handed.small_call_route is not None:
        record["smallCallRoute"] = handed.small_call_route
    record["workingFolder"] = handed.working_folder
    record["signsOfLife"] = {"heartbeat": 0, "waitingFor": "database", "since": iso()}
    try:
        folder = await claim_folder(prepared.root.exchanges, exchange, record, started + ACCEPTANCE_SECONDS)
    except Refusal as refusal:
        if handed.exchange is not None and refusal.code == "in_progress":
            prior = await find_prior(connect, handed.exchange, started + ACCEPTANCE_SECONDS)
            if prior is not None:
                raise Repeated(prepared.root.identifier, prior) from None
        raise
    accepted_at = datetime.now(UTC)
    try:
        connection, accepted = await accept_in_database(connect, Acceptance(
            exchange, chat, message, CODE_NAME, build, handed.route, handed.small_call_route,
            handed.working_folder, accepted_at, handed.replaces), started + ACCEPTANCE_SECONDS)
    except DuplicateExchange as duplicate:
        folder.discard()
        raise Repeated(prepared.root.identifier, duplicate.prior) from None
    except BaseException:
        folder.discard()
        raise
    folder.update(acceptedAt=iso(accepted_at))
    line = acceptance_line(root=prepared.root.identifier, exchange=exchange, chat=chat, number=accepted.number,
                           build=build)
    return Exchange(folder, connection, chat, accepted.number, message,
                    make_history(accepted.history, before=accepted.number), line)
