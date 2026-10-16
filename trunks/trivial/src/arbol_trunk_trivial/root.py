"""How the Trivial Trunk finds its Root's folder and database (RCT-0).

1. The Root's folder is `~/Library/Application Support/Arbol/roots/<root>/`; its `root.json` names the database and
   the version of the Root Contract the Root uses.
2. The address of the database server is `address` in `~/.arbol/database.json`, whose user is the database role.
3. The password is the Keychain item `com.sylvan-stack.arbol.database` with that role as its account, read with
   `security` within 2 seconds; the exit status 44 means there is no such item, and the Trunk connects without one.

Every file is reached from the home folder, so a test gives the Trunk a home of its own (RCT-D7, RCT-D29).
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from psycopg.conninfo import conninfo_to_dict

from .errors import Refusal

ROOT_CONTRACTS = (1,)  # the versions of the Root Contract this Trunk implements, as arbol-build.json lists them (TRV-D14)
KEYCHAIN_SERVICE = "com.sylvan-stack.arbol.database"
KEYCHAIN_SECONDS = 2.0  # not divided by ARBOL_TEST_TIME_SCALE (RCT-4)
NO_SUCH_ITEM = 44
SECURITY = "/usr/bin/security"


@dataclass(frozen=True)
class Root:
    identifier: str
    folder: Path
    database: str
    root_contract: int

    @property
    def exchanges(self) -> Path:
        return self.folder / "exchanges"


def roots_folder(home: Path) -> Path:
    return home / "Library" / "Application Support" / "Arbol" / "roots"


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def find_root(home: Path, identifier: str) -> Root:
    """The Root's folder and its record; `unknown_root` without a readable `root.json`, `contract_mismatch` when its
    version is not one this Trunk implements."""
    folder = roots_folder(home) / identifier
    try:
        record = read_json(folder / "root.json")
    except (OSError, ValueError):
        raise Refusal("unknown_root", f"The Root {identifier} has no readable root.json in {folder}.") from None
    database = record.get("database") if isinstance(record, dict) else None
    version = record.get("rootContract") if isinstance(record, dict) else None
    if not isinstance(database, str) or not database or not isinstance(version, int) or isinstance(version, bool):
        raise Refusal("unknown_root", f"The root.json of the Root {identifier} names no database or rootContract.")
    if version not in ROOT_CONTRACTS:
        raise Refusal("contract_mismatch", f"The Root {identifier} uses Root Contract version {version}; this Build "
                                           f"implements {', '.join(str(v) for v in ROOT_CONTRACTS)}.")
    return Root(identifier, folder, database, version)


def database_address(home: Path) -> str:
    """`address` in `~/.arbol/database.json`."""
    file = home / ".arbol" / "database.json"
    try:
        settings = read_json(file)
    except (OSError, ValueError):
        raise Refusal("database_unavailable", f"{file} cannot be read.") from None
    address = settings.get("address") if isinstance(settings, dict) else None
    if not isinstance(address, str) or not address:
        raise Refusal("database_unavailable", f"{file} names no address.")
    return address


def role(address: str) -> str:
    """The database role, the user that the address names."""
    try:
        user = conninfo_to_dict(address).get("user")
    except Exception:
        raise Refusal("database_unavailable", "The address in ~/.arbol/database.json cannot be read.") from None
    if not isinstance(user, str) or not user:
        raise Refusal("database_unavailable", "The address in ~/.arbol/database.json names no user.")
    return user


def keychain_password(account: str, security: str = SECURITY) -> str | None:
    """The password of the Keychain item for the role, or None when there is no such item (exit status 44)."""
    try:
        completed = subprocess.run([security, "find-generic-password", "-s", KEYCHAIN_SERVICE, "-a", account, "-w"],
                                   stdin=subprocess.DEVNULL, capture_output=True, timeout=KEYCHAIN_SECONDS)
    except subprocess.TimeoutExpired:
        raise Refusal("database_unavailable", f"The Keychain gave no answer for {KEYCHAIN_SERVICE} within "
                                              f"{KEYCHAIN_SECONDS:g} seconds.") from None
    except OSError as error:
        raise Refusal("database_unavailable", f"The Keychain cannot be read: {error.strerror}.") from None
    if completed.returncode == NO_SUCH_ITEM:
        return None
    if completed.returncode != 0:
        raise Refusal("database_unavailable", f"Reading the Keychain item {KEYCHAIN_SERVICE} failed with the exit "
                                              f"status {completed.returncode}.")
    return completed.stdout.decode("utf-8").removesuffix("\n")
