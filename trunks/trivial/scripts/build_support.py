"""Local Build metadata and integrity helpers (TRV-0, TRV-D20)."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = "arbol-trunk/trivial"
PROJECT = "arbol-trunk-trivial"
ENTRY = "bin/arbol-trunk-trivial"
NUMBER = re.compile(r"[1-9a-f][0-9a-f]*\Z", re.ASCII)


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must hold an object.")
    return value


def metadata(root: Path = ROOT) -> tuple[str, dict[str, Any], str]:
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    package = read_object(root / "package.json")
    version = project.get("version")
    pin = read_object(root / "scripts/python-distribution.json")
    if (project.get("name") != PROJECT or not isinstance(version, str)
            or package.get("version") != version):
        raise ValueError("The project and package metadata must name this Trunk and agree on its version.")
    if (project.get("requires-python") != "==" + str(pin.get("version"))
            or (root / ".python-version").read_text().strip() != pin.get("version")):
        raise ValueError("The project must use the exact pinned Python version.")
    lock = tomllib.loads((root / "uv.lock").read_text())
    versions = {item["name"]: item["version"] for item in lock["package"] if "version" in item}
    psycopg = versions.get("psycopg")
    if (not isinstance(psycopg, str) or versions.get("psycopg-binary") != psycopg
            or project.get("dependencies") != [f"psycopg[binary]=={psycopg}"]):
        raise ValueError("The only runtime dependencies must be the matching, locked psycopg binary pair.")
    return version, pin, psycopg


def build_folder(candidate: str | None = None, *, root: Path = ROOT) -> tuple[Path, str]:
    raw = candidate if candidate is not None else os.environ.get("ARBOL_BUILD_DIR", "")
    if not raw or not Path(raw).is_absolute():
        raise ValueError("The Build folder must be absolute: ARBOL_BUILD_DIR or --candidate.")
    folder = Path(raw).resolve(strict=True)
    if candidate is not None:
        if (folder / "build.json").exists():
            raise ValueError("A candidate cannot replace a numbered Build.")
        return folder, "0"
    number = os.environ.get("ARBOL_BUILD_NUMBER", "")
    record = read_object(folder / "build.json")
    version, _pin, _psycopg = metadata(root)
    if (not NUMBER.fullmatch(number) or record.get("build") != number
            or record.get("component") != COMPONENT or record.get("entry") != ENTRY
            or record.get("packageVersion") != version or record.get("rootContracts") != [1]):
        raise ValueError("The numbered Build record must match the Trunk, entry, version and Root Contracts.")
    return folder, number


def target() -> str:
    architecture = {"arm64": "aarch64", "aarch64": "aarch64", "x86_64": "x86_64"}.get(platform.machine())
    if sys.platform != "darwin" or architecture is None:
        raise ValueError("The pinned runtime supports macOS arm64 and x86_64.")
    return architecture + "-apple-darwin"


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_provenance(root: Path = ROOT) -> dict[str, Any]:
    def git(*args: str) -> str | None:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=15, check=False)
        return result.stdout.strip() if result.returncode == 0 else None

    prefix = git("rev-parse", "--show-prefix")
    return {"repository": str(root.resolve()), "commit": git("rev-parse", "HEAD"),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "uncommittedChanges": bool(git("status", "--porcelain")),
            "componentPath": prefix.rstrip("/") if prefix is not None else "/".join(root.parts[-2:])}
