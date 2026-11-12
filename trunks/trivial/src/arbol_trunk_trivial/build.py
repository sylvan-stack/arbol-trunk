"""Which Build runs (BLD-0.14): the build number comes from the record `build.json` in the Build's own folder.

Outside a Build's folder, as when the Trunk runs from its checkout, the build number is `0`.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

from . import NAME

BUILD_NUMBER = re.compile(r"(0|[1-9a-f][0-9a-f]*)", re.ASCII)
PROJECT = "arbol-trunk-trivial"
MAX_SAFE_INTEGER = 2**53 - 1

type Compatibility = dict[int, int]


class BuildRecordError(Exception):
    """The Build record in the program's own folder cannot be read or is not a record of this Trunk."""


def schema_compatibility(value: object) -> Compatibility:
    if not isinstance(value, list) or not value:
        raise ValueError("A Trivial Build must declare schemaCompatibility.")
    result: Compatibility = {}
    for item in value:
        if not isinstance(item, dict) or set(item) != {"compatibilityVersion", "minRevision"}:
            raise ValueError("Invalid schemaCompatibility entry.")
        version, minimum = item["compatibilityVersion"], item["minRevision"]
        if (type(version) is not int or not 1 <= version <= MAX_SAFE_INTEGER or version in result
                or type(minimum) is not int or not 1 <= minimum <= MAX_SAFE_INTEGER):
            raise ValueError("Invalid schemaCompatibility pair.")
        result[version] = minimum
    return result


def source_compatibility(folder: Path) -> Compatibility:
    value = json.loads((folder / "arbol-build.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("component") != NAME:
        raise ValueError("The Build description must name this Trunk.")
    return schema_compatibility(value.get("schemaCompatibility"))


def build_location(start: Path | None) -> tuple[Path | None, dict[str, Any] | None]:
    """Find the nearest matching numbered Build or the component's project directory."""
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
            return folder, record
        project_file = folder / "pyproject.toml"
        if project_file.exists():
            try:
                project = tomllib.loads(project_file.read_text(encoding="utf-8")).get("project", {})
            except (OSError, ValueError):
                project = {}
            if isinstance(project, dict) and project.get("name") == PROJECT:
                return folder, None
    return None, None


def build_number(start: Path | None = None) -> str:
    """Use the registry number of a packaged Build and 0 for a checkout or candidate."""
    _, record = build_location(start)
    return str(record["build"]) if record is not None else "0"


def build_info(start: Path | None = None) -> tuple[str, Compatibility]:
    """Read the executable's declaration and require its package and registry to agree."""
    folder, record = build_location(start)
    if folder is None:
        raise BuildRecordError("Cannot locate the Trivial Trunk Build description.")
    number = str(record["build"]) if record is not None else "0"
    try:
        declared = source_compatibility(folder)
        manifest_path = folder / "package-manifest.json"
        if record is not None or manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if (not isinstance(manifest, dict) or manifest.get("component") != NAME
                    or manifest.get("build") != number
                    or schema_compatibility(manifest.get("schemaCompatibility")) != declared):
                raise ValueError("The package and executable declarations differ.")
        if record is not None and schema_compatibility(record.get("schemaCompatibility")) != declared:
            raise ValueError("The registry and executable declarations differ.")
    except (OSError, ValueError):
        raise BuildRecordError("Cannot verify the Trivial Build's schema compatibility declaration.") from None
    return number, declared
