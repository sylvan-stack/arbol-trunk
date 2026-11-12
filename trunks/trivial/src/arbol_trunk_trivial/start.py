"""What a start reads before it accepts: the installed context and the Driver it will use (RCT-0)."""

from __future__ import annotations

from dataclasses import dataclass

from .command import Handed
from .errors import invalid
from .root import Installation
from .settings import default_driver


@dataclass(frozen=True)
class Prepared:
    handed: Handed
    root: Installation
    driver: str  # the route's driver, else the one the settings file names


def prepare(handed: Handed, context: Installation) -> Prepared:
    driver = handed.route.get("driver") or default_driver(context.home)
    if driver is None:
        raise invalid('No Driver was handed, and ~/.arbol/arbol-trunk/trivial.json names none under "driver".')
    return Prepared(handed, context, driver)
