"""Accepting a message (RCT-2, "Accepting a message").

The folder is made first, with a record that has no `acceptedAt`; then one transaction writes the chat, the open
Exchange and the message, and reads the history. All the work with the database for the acceptance ends within 10
seconds of the start, or the message is refused with `database_unavailable`; a busy chat is refused with `chat_busy`.
"""

from __future__ import annotations

import asyncio
import time

from .database import Acceptance, Accepted, ChatBusy, Connect, Connection, DatabaseUnavailable
from .errors import Refusal

ACCEPTANCE_SECONDS = 10.0  # from the start; not divided by ARBOL_TEST_TIME_SCALE (RCT-4)


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
