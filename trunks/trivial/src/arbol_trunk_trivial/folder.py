"""The Exchange folder and its record (RCT-1).

The folder is made as `.<exchange>.new` with `record.json` without `acceptedAt`, an empty `events.jsonl` and an empty
`control`, and renamed to `<exchange>`; once the database holds the Exchange's end, it is renamed to `.<exchange>.old`
and deleted. The folder has the mode 0700 and its files 0600. The record is replaced whole, by renaming
`record.json.new` over it, and who runs the Exchange never changes in it.
"""

from __future__ import annotations

import errno
import json
import os
import shutil
from pathlib import Path
from typing import Any

from .errors import Refusal

FILE_MODE = 0o600
FOLDER_MODE = 0o700
FIXED = ("rootContract", "root", "exchange", "chat", "trunk", "build", "process", "route", "smallCallRoute",
         "workingFolder")
ORDER = (*FIXED, "acceptedAt", "signsOfLife", "end")  # the order of RCT-1's example


def ordered(record: dict[str, Any]) -> dict[str, Any]:
    known = {name: record[name] for name in ORDER if name in record}
    return {**known, **{name: value for name, value in record.items() if name not in known}}


def write_file(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, FILE_MODE)
    try:
        os.fchmod(descriptor, FILE_MODE)
        view = memoryview(data)
        while view:
            view = view[os.write(descriptor, view):]
    finally:
        os.close(descriptor)


def encode(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8", "surrogatepass")


class ExchangeFolder:
    """One Exchange's folder while it runs, and the record the Trunk alone writes into it."""

    def __init__(self, exchanges: Path, exchange: str, record: dict[str, Any]) -> None:
        self.exchanges = exchanges
        self.exchange = exchange
        self.path = exchanges / exchange
        self.record = dict(record)

    @classmethod
    def make(cls, exchanges: Path, exchange: str, record: dict[str, Any]) -> ExchangeFolder:
        """Makes `.<exchange>.new` with its three files and renames it into place; `in_progress` when a folder of
        either name is there already, `trunk_failed` when it cannot be made."""
        folder = cls(exchanges, exchange, record)
        new = exchanges / f".{exchange}.new"
        if folder.path.exists():
            raise Refusal("in_progress", f"Another start of the Exchange {exchange} is accepting it.")
        try:
            os.mkdir(new, FOLDER_MODE)
        except FileExistsError:
            raise Refusal("in_progress", f"Another start of the Exchange {exchange} is accepting it.") from None
        except OSError as error:
            raise Refusal("trunk_failed", f"The Exchange's folder cannot be made: {error.strerror}.") from None
        try:
            os.chmod(new, FOLDER_MODE)
            write_file(new / "record.json", encode(folder.record) + b"\n")
            write_file(new / "events.jsonl", b"")
            write_file(new / "control", b"")
            os.rename(new, folder.path)
        except OSError as error:
            shutil.rmtree(new, ignore_errors=True)
            if error.errno in (errno.ENOTEMPTY, errno.EEXIST):
                raise Refusal("in_progress", f"Another start of the Exchange {exchange} is accepting it.") from None
            raise Refusal("trunk_failed", f"The Exchange's folder cannot be made: {error.strerror}.") from None
        return folder

    def update(self, **fields: Any) -> None:
        """Replaces the record whole with these fields changed; the fields of who runs it never change."""
        changed = [name for name in fields if name in FIXED]
        if changed:
            raise ValueError(f"The record's {', '.join(changed)} never change.")
        record = ordered({**self.record, **fields})
        new = self.path / "record.json.new"
        write_file(new, encode(record) + b"\n")
        os.replace(new, self.path / "record.json")
        self.record = record

    def remove(self) -> None:
        """Renames the folder to `.<exchange>.old` and deletes it."""
        old = self.exchanges / f".{self.exchange}.old"
        os.rename(self.path, old)
        shutil.rmtree(old)

    def discard(self) -> None:
        """Removes a folder whose Exchange the database never had, as after a refusal."""
        try:
            self.remove()
        except OSError:
            shutil.rmtree(self.path, ignore_errors=True)
