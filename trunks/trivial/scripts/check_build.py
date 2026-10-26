"""Verify this package and run its checks with its own interpreter (TRV-0)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.build_support import COMPONENT, ENTRY, build_folder, digest, metadata, read_object, target  # noqa: E402
from scripts.package_build import MUTABLE  # noqa: E402


def verify(folder: Path, *, candidate: bool) -> dict[str, Any]:
    folder = folder.resolve()
    version, pin, psycopg = metadata(folder)
    value = read_object(folder / "package-manifest.json")
    if (value.get("format") != 1 or value.get("component") != COMPONENT or value.get("entry") != ENTRY
            or value.get("packageVersion") != version or value.get("rootContracts") != [1]
            or value.get("candidate") is not candidate
            or value.get("dependencies") != {"psycopg": psycopg, "psycopg-binary": psycopg}):
        raise ValueError("The package manifest does not match the Trunk's metadata.")
    if candidate:
        if value.get("build") != "0" or (folder / "build.json").exists():
            raise ValueError("A candidate must remain Build 0 outside a numbered Build.")
    else:
        record = read_object(folder / "build.json")
        if (record.get("component") != COMPONENT or record.get("build") != value.get("build")
                or record.get("entry") != ENTRY or record.get("packageVersion") != version
                or record.get("rootContracts") != [1]):
            raise ValueError("The package and numbered Build record differ.")
    python = value.get("python")
    architecture = target()
    distribution = pin["distributions"][architecture]
    if (not isinstance(python, dict) or python.get("version") != pin["version"]
            or python.get("target") != architecture or python.get("provider") != pin["provider"]
            or python.get("release") != pin["release"] or python.get("archiveUrl") != distribution["url"]
            or python.get("archiveSha256") != distribution["sha256"]
            or python.get("executable") != "runtime/python/bin/python3.14"):
        raise ValueError("The runtime does not match the pinned distribution.")
    files = value.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("The package must list its file digests.")
    actual = {str(path.relative_to(folder)): path for path in folder.rglob("*") if path.is_file()
              and str(path.relative_to(folder)) not in MUTABLE}
    if set(actual) != set(files):
        raise ValueError("The package's file set changed.")
    for name, expected in files.items():
        path = actual[name]
        if (not path.resolve().is_relative_to(folder) or not isinstance(expected, str)
                or digest(path) != expected):
            raise ValueError(f"The package file {name} escaped its folder or changed.")
    interpreter = folder / python["executable"]
    if digest(interpreter) != python.get("executableSha256"):
        raise ValueError("The packaged interpreter changed.")
    entry = folder / ENTRY
    if not entry.is_file() or not os.access(entry, os.X_OK) or entry.is_symlink():
        raise ValueError("The Build entry must be its own executable file.")
    return value


def unit(folder: Path) -> int:
    sys.path.insert(0, str(folder))
    sys.path.insert(0, str(folder / "src"))
    suite = unittest.TestLoader().discover(str(folder / "tests"))
    if suite.countTestCases() == 0:
        raise ValueError("The packaged unit suite has no tests.")
    return 0 if unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful() else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("metadata", "unit"))
    parser.add_argument("--candidate", help="Absolute development package folder")
    args = parser.parse_args()
    try:
        folder, _number = build_folder(args.candidate)
        value = verify(folder, candidate=args.candidate is not None)
        interpreter = folder / "runtime/python/bin/python3.14"
        if Path(sys.executable).resolve() != interpreter.resolve():
            command = [str(interpreter), "-I", "-B", str(folder / "scripts/check_build.py"), args.mode]
            if args.candidate is not None:
                command += ["--candidate", str(folder)]
            return subprocess.run(command, cwd=folder, check=False).returncode
        if args.mode == "metadata":
            print(json.dumps({"component": COMPONENT, "build": value["build"], "python": value["python"], "passed": True}))
            return 0
        status = unit(folder)
        verify(folder, candidate=args.candidate is not None)
        return status
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"Cannot check {COMPONENT}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
