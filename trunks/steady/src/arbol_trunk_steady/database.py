"""Bounded PostgreSQL operations against the installed database."""

from __future__ import annotations

import asyncio
import os
import re
import tomllib
from collections.abc import AsyncIterator, Awaitable, Callable, Coroutine, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Protocol

import psycopg
from psycopg import errors as sqlstate
from psycopg.conninfo import make_conninfo
from psycopg.types.json import Jsonb

from . import NAME
from .admission import DATABASE_WRITER_LOCK, Lease
from .build import Compatibility
from .errors import Refusal
from .history import HistoryRow
from .root import Installation, keychain_password
from .rows import Row, RunRow, jsonb, row_line
from .storage import stored

CALL_SECONDS = 5.0


class DatabaseUnavailable(Exception):
    """A call to the database failed or did not end within its limit; the connection is given up."""


class AcceptanceUncertain(DatabaseUnavailable):
    """Acceptance reached COMMIT, whose outcome could not be confirmed."""


class SchemaRefusal(DatabaseUnavailable):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code

    def refusal(self) -> Refusal:
        return Refusal(self.code, str(self))


class RowRejected(Exception):
    """A row's value or constraint will fail on every retry (SQLSTATE class 22 or 23)."""

    def __init__(self, row: Row) -> None:
        self.line = row_line(row)
        super().__init__(f"The database refused the row from line {self.line}.")


def permanent(error: DatabaseUnavailable) -> bool:
    cause = error.__cause__
    return isinstance(cause, psycopg.Error) and str(cause.sqlstate)[:2] in {"22", "23"}


class ChatBusy(Exception):
    """The chat has an open Exchange, or another message to it was accepted at the same moment (RCT-2)."""

    def __init__(self, open_exchange: str | None) -> None:
        super().__init__(open_exchange)
        self.open_exchange = open_exchange


@dataclass(frozen=True)
class Acceptance:
    """What the acceptance writes: the chat when it is new, the open Exchange, and the message at position 0."""

    exchange: str
    chat: str
    message: str
    trunk: str
    build: str
    route: dict[str, Any]
    small_call_route: dict[str, Any] | None
    working_folder: str
    accepted_at: datetime
    replaces: str | None = None


@dataclass(frozen=True)
class Accepted:
    number: int  # the Exchange's place in its chat
    history: list[HistoryRow]  # the rows of the chat's earlier Exchanges, read in the same transaction


@dataclass(frozen=True)
class StoredExchange:
    state: str
    accepted_at: datetime
    ended_at: datetime | None = None
    error: dict[str, Any] | None = None


@dataclass(frozen=True)
class PriorExchange:
    exchange: str
    chat: str
    number: int
    trunk: str
    build: str


class DuplicateExchange(Exception):
    def __init__(self, prior: PriorExchange) -> None:
        self.prior = prior


@dataclass(frozen=True)
class Replacement:
    chat: str
    message: str


class ReplacementRefused(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def checked_replacement(found: Sequence[Any] | None) -> Replacement:
    if found is None:
        raise ReplacementRefused("not_found", "The Exchange to replace does not exist.")
    chat, state, replaced_by, number, last, message = found
    if state == "open" or replaced_by is not None or number != last:
        raise ReplacementRefused("cannot_replace", "Only the chat's last ended, unreplaced Exchange can be sent again.")
    if message is None:
        raise ReplacementRefused("trunk_failed", "The Exchange to replace has no stored message.")
    return Replacement(str(chat), str(message))


class Connection(Protocol):
    """The calls the Trunk makes on the installed database."""

    async def accept(self, acceptance: Acceptance) -> Accepted: ...

    async def save(self, row: Row) -> None: ...

    async def exchange_state(self, exchange: str) -> StoredExchange | None: ...

    async def find_exchange(self, exchange: str) -> PriorExchange | None: ...

    async def replacement(self, exchange: str) -> Replacement: ...

    async def end(self, exchange: str, rows: list[Row], state: str, ended_at: datetime,
                  error: dict[str, Any] | None, *, end_written: bool = True) -> None: ...

    async def close(self) -> None: ...


Connect = Callable[[], Coroutine[Any, Any, Connection]]
type LedgerRow = tuple[int, str, str, int]


def release_history(path: Path) -> tuple[LedgerRow, ...]:
    """The expected history comes from the installed release and can advance independently of this Build."""
    try:
        with path.open("rb") as stream:
            manifest = tomllib.load(stream)
        entries = manifest["migrations"]
        if (set(manifest) != {"format", "migrations"} or type(manifest["format"]) is not int
                or manifest["format"] != 1 or not isinstance(entries, list)):
            raise ValueError
        rows: list[LedgerRow] = []
        identities: set[str] = set()
        filenames: set[str] = set()
        for number, entry in enumerate(entries, 1):
            if not isinstance(entry, dict) or set(entry) != {
                    "revision", "predecessor", "id", "file", "sha256", "compatibility_version"}:
                raise ValueError
            revision, predecessor = entry["revision"], entry["predecessor"]
            name, digest, version = entry["id"], entry["sha256"], entry["compatibility_version"]
            filename = entry["file"]
            previous = rows[-1][3] if rows else 0
            if (type(revision) is not int or revision != number
                    or type(predecessor) is not int or predecessor != number - 1
                    or not isinstance(name, str) or re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name) is None
                    or name in identities
                    or not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None
                    or not isinstance(filename, str) or re.fullmatch(r"[a-zA-Z0-9_-]+\.sql", filename) is None
                    or filename in filenames
                    or type(version) is not int or version < 1 or version not in (previous, previous + 1)):
                raise ValueError
            migration = path.with_name(filename)
            if migration.is_symlink() or sha256(migration.read_bytes()).hexdigest() != digest:
                raise ValueError
            rows.append((revision, name, digest, version))
            identities.add(name)
            filenames.add(filename)
        if rows:
            return tuple(rows)
    except (OSError, ValueError, KeyError, TypeError):
        pass
    raise Refusal("schema_invalid", "The installed Arbol migration manifest is unreadable.")


@dataclass(frozen=True)
class SchemaGuard:
    database: str
    history: tuple[LedgerRow, ...]
    compatibility: Compatibility

    async def require(self, connection: psycopg.AsyncConnection[Any]) -> tuple[int, int]:
        """Verify the ledger and return (revision, compatibility version) on the writer's connection."""
        if connection.info.dbname != self.database:
            raise SchemaRefusal("database_unavailable", "PostgreSQL did not connect to the configured Arbol database.")
        try:
            async with connection.cursor() as cursor:
                await within_limit(cursor.execute(
                    "SELECT revision, migration_id, checksum, compatibility_version "
                    "FROM public.arbol_schema_migrations "
                    "WHERE (SELECT count(*) FROM pg_catalog.pg_class c "
                    "JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relpersistence = 'p' "
                    "AND c.relname IN ('arbol_schema_migrations', 'arbol_schema_upgrades')) = 2 "
                    "ORDER BY revision LIMIT %s",
                    (len(self.history) + 1,)))
                rows = await within_limit(cursor.fetchall())
        except DatabaseUnavailable as error:
            if isinstance(error.__cause__, sqlstate.UndefinedTable):
                raise SchemaRefusal("schema_uninitialized", "The installed Arbol database has no schema ledger.") from None
            if isinstance(error.__cause__, (sqlstate.UndefinedColumn, sqlstate.InsufficientPrivilege)):
                raise SchemaRefusal("schema_invalid", "The installed Arbol migration ledger is unreadable.") from None
            raise
        if (not rows or tuple(rows) != self.history[:len(rows)]
                or any(type(row[0]) is not int or type(row[3]) is not int for row in rows)):
            raise SchemaRefusal("schema_invalid", "The installed Arbol migration ledger does not match this release.")
        revision, _, _, version = self.history[len(rows) - 1]
        minimum = self.compatibility.get(version)
        if minimum is None or revision < minimum:
            raise SchemaRefusal("schema_incompatible", f"This Trunk Build cannot use Arbol schema revision {revision} "
                                                     f"with compatibility version {version}.")
        return revision, version


def installed_postgres(context: Installation, security: str, compatibility: Compatibility,
                       *, lease: Lease | None = None) -> Connect:
    """Use the same explicit target as status, with credentials scoped to libpq."""
    if lease is None:
        raise Refusal("maintenance", "No installation writer permit was supplied.")
    lease.require()
    target = context.target
    password = None if target.socket else keychain_password(target.account, security)
    if "PGSERVICE" in os.environ or (not target.socket and not password):
        raise Refusal("database_unavailable", "Cannot resolve the installed database credential and connection.")
    info = make_conninfo(dbname=target.name, user=target.account, host=target.host, port=target.port,
                         hostaddr="" if target.socket else target.host, password="" if target.socket else password,
                         passfile=os.devnull, sslmode="disable", gssencmode="disable", target_session_attrs="any",
                         client_encoding="UTF8", connect_timeout=int(CALL_SECONDS), application_name=NAME,
                         options=f"-csearch_path=public -cstatement_timeout={int(CALL_SECONDS * 1000)}")
    manifest = context.bin_dir / ".arbol-builds/schema/migrations.toml"
    return postgres(info, guard=SchemaGuard(target.name, release_history(manifest), compatibility), lease=lease)


async def preflight(connect: Connect, deadline: float) -> None:
    """Check before the first local file effect as well as checking each production connection."""
    try:
        async with asyncio.timeout_at(deadline):
            connection = await connect()
    except SchemaRefusal as error:
        raise error.refusal() from None
    except (DatabaseUnavailable, TimeoutError):
        raise Refusal("database_unavailable", "The installed Arbol database did not answer.") from None
    await connection.close()


def conninfo(address: str, database: str, password: str | None) -> str:
    extra: dict[str, Any] = {"dbname": database, "connect_timeout": int(CALL_SECONDS), "application_name": NAME,
                             "options": f"-c statement_timeout={int(CALL_SECONDS * 1000)}"}
    if password is not None:
        extra["password"] = password
    return make_conninfo(address, **extra)


async def within_limit[T](call: Awaitable[T]) -> T:
    try:
        return await asyncio.wait_for(call, CALL_SECONDS)
    except TimeoutError:
        raise DatabaseUnavailable(f"The database did not answer within {CALL_SECONDS:g} seconds.") from None
    except psycopg.Error as error:
        raise DatabaseUnavailable(str(error).strip() or type(error).__name__) from error


@asynccontextmanager
async def transaction(connection: psycopg.AsyncConnection[Any], *, acceptance: bool = False) -> AsyncIterator[None]:
    """Bound transaction commands too: BEGIN, SAVEPOINT, rollback and COMMIT can each lose the server."""
    work = connection.transaction()
    await within_limit(work.__aenter__())
    try:
        yield
    except BaseException as error:
        await within_limit(work.__aexit__(type(error), error, error.__traceback__))
        raise
    else:
        try:
            await within_limit(work.__aexit__(None, None, None))
        except (DatabaseUnavailable, asyncio.CancelledError) as error:
            if acceptance:
                raise AcceptanceUncertain() from error
            raise


BUSY = ("exchanges_one_open_per_chat", "exchanges_chat_id_number_key")

HISTORY = """
SELECT e.number, m.position, e.replaced_by IS NOT NULL, m.role, m.text,
       NULL::text, NULL::jsonb, NULL::boolean, NULL::jsonb, NULL::text, NULL::text
  FROM exchanges e JOIN messages m ON m.exchange_id = e.id
 WHERE e.chat_id = %(chat)s AND e.number < %(number)s AND e.replaced_by IS NULL
UNION ALL
SELECT e.number, t.position, e.replaced_by IS NOT NULL, NULL, NULL,
       t.name, t.input, t.ok, t.result, t.error, t.parent_call_id
  FROM exchanges e JOIN tool_calls t ON t.exchange_id = e.id
 WHERE e.chat_id = %(chat)s AND e.number < %(number)s AND e.replaced_by IS NULL AND t.parent_call_id IS NULL
 ORDER BY 1, 2
"""


class PostgresConnection:
    def __init__(self, connection: psycopg.AsyncConnection[Any], guard: SchemaGuard | None = None,
                 lease: Lease | None = None) -> None:
        self.connection = connection
        self.guard = guard
        self.lease = lease

    def require_lease(self) -> None:
        if self.lease is not None:
            try:
                self.lease.require()
            except Refusal as error:
                raise SchemaRefusal(error.code, str(error)) from None

    async def admit(self) -> None:
        if self.lease is None:
            return
        self.require_lease()
        raw = self.connection
        source = self.lease.state.source
        # Register on the server before sending any statement that could write.
        # This lease survives a lost client long enough to finish server work.
        cursor = await within_limit(raw.execute("SELECT pg_catalog.pg_try_advisory_lock_shared(%s::bigint)",
                                                (DATABASE_WRITER_LOCK,)))
        if await within_limit(cursor.fetchone()) != (True,):
            raise SchemaRefusal("maintenance", "PostgreSQL is fenced for migration.")
        cursor = await within_limit(raw.execute(
            "SELECT oid FROM pg_catalog.pg_database WHERE datname = pg_catalog.current_database()"))
        if (raw.info.host != source["host"] or raw.info.port != source["port"]
                or raw.info.dbname != source["database"]
                or await within_limit(cursor.fetchone()) != (source["databaseOid"],)):
            raise SchemaRefusal("maintenance", "The configured database does not match the writer admission target.")

    async def accept(self, acceptance: Acceptance) -> Accepted:
        """One transaction: the chat with an insert that does nothing when it is there, the open Exchange with the
        next number in its chat, the message at position 0, and the history of the chat (RCT-2, TRV-D3)."""
        a = acceptance
        self.require_lease()
        try:
            async with transaction(self.connection, acceptance=True), self.connection.cursor() as cursor:
                if self.guard is not None:
                    await self.guard.require(self.connection)
                await self.lock_exchange(a.exchange)
                await within_limit(cursor.execute(
                    "INSERT INTO chats (id, created_at) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (a.chat, a.accepted_at)))
                await within_limit(cursor.execute("SELECT id FROM chats WHERE id = %s FOR UPDATE", (a.chat,)))
                message = a.message
                if a.replaces is not None:
                    prior = await self.find_exchange(a.exchange)
                    if prior is not None:
                        raise DuplicateExchange(prior)
                    replacement = await self.replacement(a.replaces)
                    if replacement.chat != a.chat:
                        raise ReplacementRefused("invalid_input", "The handed chat differs from the replaced Exchange's chat.")
                    message = replacement.message
                await within_limit(cursor.execute(
                    "SELECT coalesce(max(number), 0) + 1 FROM exchanges WHERE chat_id = %s", (a.chat,)))
                found = await cursor.fetchone()
                number = int(found[0]) if found else 1
                await within_limit(cursor.execute(
                    "INSERT INTO exchanges (id, chat_id, number, state, trunk, build, route, small_call_route,"
                    " working_folder, accepted_at) VALUES (%s, %s, %s, 'open', %s, %s, %s, %s, %s, %s)",
                    stored((a.exchange, a.chat, number, a.trunk, a.build, Jsonb(a.route),
                     None if a.small_call_route is None else Jsonb(a.small_call_route), a.working_folder,
                     a.accepted_at))))
                await within_limit(cursor.execute(
                    "INSERT INTO messages (exchange_id, position, role, text) VALUES (%s, 0, 'user', %s)",
                    stored((a.exchange, message))))
                if a.replaces is not None:
                    await within_limit(cursor.execute("UPDATE exchanges SET replaced_by = %s WHERE id = %s",
                                                      (a.exchange, a.replaces)))
                    await within_limit(cursor.execute("DELETE FROM messages WHERE exchange_id = %s", (a.replaces,)))
                    await within_limit(cursor.execute("DELETE FROM tool_calls WHERE exchange_id = %s", (a.replaces,)))
                await within_limit(cursor.execute(HISTORY, {"chat": a.chat, "number": number}))
                rows = await cursor.fetchall()
        except DatabaseUnavailable as error:
            if isinstance(error.__cause__, sqlstate.UniqueViolation):
                prior = await self.find_exchange(a.exchange)
                if prior is not None:
                    raise DuplicateExchange(prior) from None
            if isinstance(error.__cause__, sqlstate.UniqueViolation) and error.__cause__.diag.constraint_name in BUSY:
                raise ChatBusy(await self.open_exchange(a.chat)) from None
            raise
        return Accepted(number, [HistoryRow(*row) for row in rows])

    async def save(self, row: Row) -> None:
        """One row, with an insert that does nothing when it is there, in a transaction of its own."""
        self.require_lease()
        sql, params = row.statement()
        try:
            await within_limit(self.connection.execute(sql, params))
        except DatabaseUnavailable as error:
            if permanent(error):
                raise RowRejected(row) from error
            raise

    async def exchange_state(self, exchange: str) -> StoredExchange | None:
        async with self.connection.cursor() as cursor:
            await within_limit(cursor.execute("SELECT state, accepted_at, ended_at, error FROM exchanges WHERE id = %s", (exchange,)))
            found = await cursor.fetchone()
        return StoredExchange(str(found[0]), found[1], found[2], found[3]) if found is not None else None

    async def lock_exchange(self, exchange: str) -> None:
        # Also used by the runtime before declaring an interrupted acceptance absent.
        await within_limit(self.connection.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (exchange,)))

    async def find_exchange(self, exchange: str) -> PriorExchange | None:
        async with transaction(self.connection), self.connection.cursor() as cursor:
            await self.lock_exchange(exchange)
            await within_limit(cursor.execute("SELECT id::text, chat_id::text, number, trunk, build"
                                              " FROM exchanges WHERE id = %s", (exchange,)))
            found = await within_limit(cursor.fetchone())
        return PriorExchange(str(found[0]), str(found[1]), int(found[2]), str(found[3]), str(found[4])) if found else None

    async def replacement(self, exchange: str) -> Replacement:
        async with self.connection.cursor() as cursor:
            await within_limit(cursor.execute(
                "SELECT e.chat_id::text, e.state, e.replaced_by, e.number,"
                " (SELECT max(number) FROM exchanges WHERE chat_id = e.chat_id), m.text"
                " FROM exchanges e LEFT JOIN messages m ON m.exchange_id = e.id AND m.position = 0"
                " WHERE e.id = %s", (exchange,)))
            found = await cursor.fetchone()
        return checked_replacement(found)

    async def end(self, exchange: str, rows: list[Row], state: str, ended_at: datetime,
                  error: dict[str, Any] | None, *, end_written: bool = True) -> None:
        """One transaction: the rows not yet saved, and the final state, changing the Exchange only while it is open
        (RCT-2.20)."""
        self.require_lease()
        async with transaction(self.connection), self.connection.cursor() as cursor:
            await within_limit(cursor.execute("SELECT replaced_by, state FROM exchanges WHERE id = %s FOR UPDATE", (exchange,)))
            found = await cursor.fetchone()
            if found is None or found[1] != "open":
                return
            replaced = found[0] is not None
            for row in tuple(rows):
                if replaced and not isinstance(row, RunRow):
                    continue
                sql, params = row.statement()
                try:
                    async with transaction(self.connection):  # a refused row rolls back only its savepoint
                        await within_limit(cursor.execute(sql, params))
                except DatabaseUnavailable as refused:
                    if not permanent(refused):
                        raise
                    rows.remove(row)  # survive a later transaction/connection failure without retrying this row
                    if not end_written:
                        state = "failed"
                        error = {"code": "trunk_failed", "message": str(RowRejected(row))}
                        end_written = True  # keep the first refused line as the cause
            await within_limit(cursor.execute(
                "UPDATE exchanges SET state = %s, ended_at = %s, error = %s WHERE id = %s AND state = 'open'",
                stored((state, ended_at, jsonb(error), exchange))))

    async def open_exchange(self, chat: str) -> str | None:
        try:
            async with self.connection.cursor() as cursor:
                await within_limit(cursor.execute(
                    "SELECT id::text FROM exchanges WHERE chat_id = %s AND state = 'open'", (chat,)))
                found = await cursor.fetchone()
        except DatabaseUnavailable:
            return None
        return str(found[0]) if found else None

    async def close(self) -> None:
        try:
            await asyncio.wait_for(self.connection.close(), 1.0)
        except (TimeoutError, psycopg.Error, OSError):
            pass


def postgres(info: str, *, guard: SchemaGuard | None = None, lease: Lease | None = None) -> Connect:
    """Verify each newly opened production connection before handing it to a writer."""

    async def connect() -> Connection:
        raw = await within_limit(psycopg.AsyncConnection.connect(info, autocommit=True))
        connection = PostgresConnection(raw, guard, lease)
        try:
            await connection.admit()
            if guard is not None:
                await guard.require(raw)
        except BaseException:
            await connection.close()
            raise
        return connection

    return connect



@asynccontextmanager
async def writer_connections(connect: Connect) -> AsyncIterator[Connect]:
    """Close any leftover writing connection before its enclosing file lease ends."""
    opened: set[PostgresConnection] = set()

    async def tracked() -> Connection:
        connection = await connect()
        opened.difference_update([old for old in opened if old.connection.closed])
        if isinstance(connection, PostgresConnection):
            opened.add(connection)
        return connection

    try:
        yield tracked
    finally:
        for connection in opened:
            if not connection.connection.closed:
                await connection.close()
