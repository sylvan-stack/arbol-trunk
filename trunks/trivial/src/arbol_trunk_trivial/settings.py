"""The Trivial Trunk's own settings file, `~/.arbol/arbol-trunk/trivial.json` (RCT-0, TRV-D7).

Its one setting, `driver`, names the Driver used when none is handed, such as `{"driver": "claude"}`. A file that is
not a JSON object with a string `driver` counts as a file without `driver`. No other settings file is read (TRV-0.9).
"""

from __future__ import annotations

import json
from pathlib import Path

from . import CODE_NAME


def settings_file(home: Path) -> Path:
    return home / ".arbol" / "arbol-trunk" / f"{CODE_NAME}.json"


def default_driver(home: Path) -> str | None:
    try:
        with settings_file(home).open(encoding="utf-8") as stream:
            settings = json.load(stream)
    except (OSError, ValueError):
        return None
    driver = settings.get("driver") if isinstance(settings, dict) else None
    return driver if isinstance(driver, str) and driver else None
