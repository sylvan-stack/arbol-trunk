"""Resolve the single installation, PostgreSQL target and private runtime directory."""

from __future__ import annotations

import ipaddress
import json
import os
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from .errors import Refusal

KEYCHAIN_SERVICE = "com.sylvan-stack.arbol.database"
KEYCHAIN_SECONDS = 2.0  # not divided by ARBOL_TEST_TIME_SCALE (RCT-4)
NO_SUCH_ITEM = 44
SECURITY = "/usr/bin/security"


@dataclass(frozen=True)
class InstalledDatabase:
    name: str
    host: str
    port: int
    account: str
    socket: bool


def installed_database(home: Path) -> InstalledDatabase:
    """Read the one target, with an owner-only socket available for an isolated installation."""
    try:
        settings = read_json(home / ".arbol/database.json")
        if not isinstance(settings, dict) or set(settings) != {"address", "database"}:
            raise ValueError
        address, name = settings["address"], settings["database"]
        if (not isinstance(address, str) or not isinstance(name, str) or not name.strip()
                or len(name.encode("utf-8")) > 63 or "\0" in name
                or name.lower() in {"postgres", "template0", "template1"}):
            raise ValueError
        url = urlsplit(address)
        if (url.scheme not in ("postgres", "postgresql") or not url.hostname or not url.username
                or not url.port or url.password is not None or url.path not in ("", "/")
                or url.query or url.fragment):
            raise ValueError
        host, account = unquote(url.hostname, errors="strict"), unquote(url.username, errors="strict")
        if not account.strip() or "\0" in account:
            raise ValueError
        socket = host.startswith("/")
        if socket:
            directory = Path(host).resolve(strict=True)
            mode = directory.stat()
            installed_socket = home / "Library/Application Support/Arbol/database/socket"
            if ("," in str(directory) or directory == installed_socket.resolve()
                    or not stat.S_ISDIR(mode.st_mode) or mode.st_uid != os.getuid() or mode.st_mode & 0o077):
                raise ValueError
            host = str(directory)
        else:
            ip = ipaddress.ip_address(host)
            if not ip.is_loopback:
                raise ValueError
            host = str(ip)
        return InstalledDatabase(name, host, url.port, account, socket)
    except (OSError, ValueError, RuntimeError):
        raise Refusal("database_unavailable", "Cannot read the installed Arbol database configuration.") from None


@dataclass(frozen=True)
class Installation:
    home: Path
    runtime: Path
    bin_dir: Path
    target: InstalledDatabase

    @property
    def exchanges(self) -> Path:
        return self.runtime / "exchanges"

    # Compatibility with the acceptance code until the versioned record lands.
    identifier = ""
    root_contract = 1


def installation(home: Path) -> Installation:
    target = installed_database(home)
    runtime = home / "Library/Application Support/Arbol/runtime"
    bin_dir = home / ".local/bin"
    if target.socket:
        runtime = Path(os.environ.get("ARBOL_EXCHANGE_RUNTIME_DIR", runtime))
        bin_dir = Path(os.environ.get("ARBOL_EXCHANGE_BIN_DIR", bin_dir))
        if not runtime.is_absolute() or not bin_dir.is_absolute():
            raise Refusal("invalid_input", "Isolated runtime and bin directories must be absolute.")
    return Installation(home, runtime, bin_dir, target)


def private_directory(path: Path) -> None:
    try:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = path.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError
    except (OSError, ValueError):
        raise Refusal("runtime_unavailable", "The Exchange runtime needs an owner-only directory.") from None


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


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
