"""Which Build runs (BLD-0.14): the build number comes from the record `build.json` in the Build's own folder.

Outside a Build's folder, as when the Trunk runs from its checkout, the build number is `0`.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from . import NAME

BUILD_NUMBER = re.compile(r"(0|[1-9a-f][0-9a-f]*)", re.ASCII)
PROJECT = "arbol-trunk-trivial"


class BuildRecordError(Exception):
    """The Build record in the program's own folder cannot be read or is not a record of this Trunk."""


def build_number(start: Path | None = None) -> str:
    """The build number of the Build that runs: from the first `build.json` of this Trunk in the folders above the
    program, or `0` once the checkout's own `pyproject.toml` is reached first."""
    directory = start or Path(__file__).resolve().parent
    for folder in (directory, *directory.parents):
        record_file = folder / "build.json"
        if record_file.exists():
            try:
                record = json.loads(record_file.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                raise BuildRecordError(f"Cannot read the Build record {record_file}.") from None
            build = record.get("build") if isinstance(record, dict) else None
            if (not isinstance(record, dict) or record.get("component") != NAME or not isinstance(build, str)
                    or BUILD_NUMBER.fullmatch(build) is None):
                raise BuildRecordError(f"The Build record {record_file} is not a record of {NAME}.")
            return build
        project_file = folder / "pyproject.toml"
        if project_file.exists():
            try:
                project = tomllib.loads(project_file.read_text(encoding="utf-8")).get("project", {})
            except (OSError, ValueError):
                project = {}
            if project.get("name") == PROJECT:
                return "0"
    return "0"
