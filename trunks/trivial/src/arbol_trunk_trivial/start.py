"""What a start reads before it accepts: the Root, the Driver it will use, and how to reach the database (RCT-0)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .command import Handed
from .errors import invalid
from .root import SECURITY, Root, database_address, find_root, keychain_password, role
from .settings import default_driver


@dataclass(frozen=True)
class Prepared:
    handed: Handed
    root: Root
    driver: str  # the route's driver, else the one the settings file names
    address: str
    password: str | None


def prepare(handed: Handed, home: Path, security: str = SECURITY) -> Prepared:
    root = find_root(home, handed.root)
    driver = handed.route.get("driver") or default_driver(home)
    if driver is None:
        raise invalid('No Driver was handed, and ~/.arbol/arbol-trunk/trivial.json names none under "driver".')
    address = database_address(home)
    return Prepared(handed, root, driver, address, keychain_password(role(address), security))
