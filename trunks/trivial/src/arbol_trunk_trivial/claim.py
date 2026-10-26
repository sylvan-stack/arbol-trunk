"""Coordinate folder claims and abandoned-start cleanup without adding a lock file (TRV-D16)."""

from __future__ import annotations

import asyncio
import fcntl
import os
import shutil
import stat
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from .errors import Refusal
from .folder import ExchangeFolder
from .process import process_alive
from .root import read_json

START_AGE_SECONDS = 15.0  # an abandoned start is not removed before the longest acceptance time (RCT-2.18)


@asynccontextmanager
async def root_lock(exchanges: Path, deadline: float) -> AsyncIterator[None]:
    try:
        descriptor = os.open(exchanges, os.O_RDONLY)
    except OSError as error:
        raise Refusal("trunk_failed", f"The Exchange folders cannot be coordinated: {error.strerror}.") from None
    try:
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise Refusal("database_unavailable", "Folder coordination exceeded the command's time budget.") from None
                await asyncio.sleep(min(0.01, max(deadline - time.monotonic(), 0)))
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def stale_folders(exchanges: Path, exchange: str) -> list[Path]:
    stale: list[Path] = []
    for path in (exchanges / exchange, exchanges / f".{exchange}.new"):
        try:
            info = path.stat(follow_symlinks=False)
        except FileNotFoundError:
            continue
        if not stat.S_ISDIR(info.st_mode):
            raise Refusal("trunk_failed", "An Exchange folder is not a directory.")
        created = getattr(info, "st_birthtime", info.st_mtime)
        if time.time() - created < START_AGE_SECONDS:
            raise Refusal("in_progress", f"Another start of the Exchange {exchange} is still accepting it.")
        try:
            record = read_json(path / "record.json")
        except (FileNotFoundError, ValueError):
            record = None
        if isinstance(record, dict) and record.get("process") is not None and process_alive(record["process"]):
            raise Refusal("in_progress", f"Another start of the Exchange {exchange} is still alive.")
        stale.append(path)
    return stale


async def claim_folder(exchanges: Path, exchange: str, record: dict[str, Any], deadline: float) -> ExchangeFolder:
    async with root_lock(exchanges, deadline):
        try:
            for path in stale_folders(exchanges, exchange):
                shutil.rmtree(path)
            return ExchangeFolder.make(exchanges, exchange, record)
        except OSError as error:
            raise Refusal("trunk_failed", f"The abandoned start cannot be removed: {error.strerror}.") from None
