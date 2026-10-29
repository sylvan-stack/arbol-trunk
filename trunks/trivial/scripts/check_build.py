# Test implementations moved to trunks/trivial/tests/mid/archived/trunks/trivial/scripts/check_build.py.
"""Verify this package and run its checks with its own interpreter (TRV-0)."""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.build_support import COMPONENT, ENTRY, build_folder, digest, metadata, read_object, target  # noqa: E402
from scripts.package_build import MUTABLE  # noqa: E402


def program_policy(folder: Path, manifest: dict[str, Any]) -> None:
    """Check the program's imports and identity without importing unchecked source (RCT-0)."""
    source = folder / "src"
    if {item.name for item in source.iterdir() if item.name != "__pycache__"} != {"arbol_trunk_trivial"}:
        raise ValueError("The package must contain only the Trivial Trunk's source.")
    if manifest.get("source", {}).get("componentPath") != "trunks/trivial":
        raise ValueError("The source must come from trunks/trivial.")
    description = read_object(folder / "arbol-build.json")
    package = read_object(folder / "package.json")
    if (description.get("component") != COMPONENT or description.get("entry") != ENTRY
            or description.get("rootContracts") != [1]
            or package.get("name") != "@sylvan-stack/arbol-trunk-trivial"
            or package.get("repository", {}).get("directory") != "trunks/trivial"):
        raise ValueError("The Build description must name this Trunk, its entry and Root Contracts.")
    allowed = sys.stdlib_module_names | {"arbol_trunk_trivial", "psycopg"}
    files = [*source.rglob("*.py"), folder / "bin/entry.py"]
    for path in files:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            imports: list[str] = []
            if isinstance(node, ast.Import):
                imports = [name.name for name in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    if not path.is_relative_to(source / "arbol_trunk_trivial") or node.level != 1:
                        raise ValueError(f"A relative import escapes this Trunk in {path.name}.")
                    continue
                imports = [node.module or ""]
            for name in imports:
                if name.split(".")[0] not in allowed:
                    raise ValueError(f"The program imports {name}, outside the standard library and psycopg.")
        if path.name in ("__init__.py", "root.py") and path.parent == source / "arbol_trunk_trivial":
            constants = {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
                         if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                         and node.targets[0].id in {"NAME", "CODE_NAME", "ROOT_CONTRACTS"}}
            if path.name == "__init__.py" and constants != {"NAME": COMPONENT, "CODE_NAME": "trivial"}:
                raise ValueError("The program's component and code name differ from its Build.")
            if path.name == "root.py" and list(constants.get("ROOT_CONTRACTS", ())) != description["rootContracts"]:
                raise ValueError("The program's Root Contracts differ from its Build.")


def runtime_probe(folder: Path) -> None:
    """The package's isolated interpreter must load binary psycopg from its own site-packages."""
    probe = '''import importlib, json, pathlib, platform, sys
folder = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(folder / "src"))
import psycopg, psycopg_binary
for path in (folder / "src/arbol_trunk_trivial").glob("*.py"):
    importlib.import_module("arbol_trunk_trivial" + ("." + path.stem if path.stem != "__init__" else ""))
site = folder / "runtime/python/lib/python3.14/site-packages"
for name, module in sys.modules.copy().items():
    if name.split(".")[0] in {"psycopg", "psycopg_binary"}:
        path = pathlib.Path(module.__file__).resolve()
        if not path.is_relative_to(site):
            raise ValueError("psycopg was loaded from outside the package")
print(json.dumps({"python": platform.python_version(), "psycopg": psycopg.__version__, "implementation": psycopg.pq.__impl__}))
'''
    result = subprocess.run([str(folder / "runtime/python/bin/python3.14"), "-I", "-B", "-c", probe, str(folder)],
                            cwd=folder, check=True, capture_output=True, text=True, timeout=30)
    _version, pin, psycopg = metadata(folder)
    if json.loads(result.stdout) != {"python": pin["version"], "psycopg": psycopg, "implementation": "binary"}:
        raise ValueError("The runtime must load the pinned Python and binary psycopg from this package.")


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
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


def live_fixture(folder: Path, owner: Path) -> Any:
    # The same external readonly checkout as contract-1. No Root code is copied into this package (TRV-D21).
    root = owner / "repos/sylvan-stack/readonly/arbol-root"
    if read_object(root / "package.json").get("name") != "@sylvan-stack/arbol-root":
        raise ValueError("The live check needs the readonly arbol-root checkout used by contract-1.")
    sys.path.insert(0, str(root / "contract/conformance"))
    fixture = importlib.import_module("rct_conformance.home").ScenarioHome
    return fixture.create("live", [str(folder / ENTRY)], 1, root / "contract/1/layout.sql",
                          python=str(folder / "runtime/python/bin/python3.14"))


def driver_bridge(launcher: Path, owner: Path, state: Path) -> None:
    driver = owner / ".local/bin/arbol-claude-driver"
    if not driver.is_file() or not os.access(driver, os.X_OK):
        raise ValueError("The live check needs the installed Claude Driver.")
    quote = shlex.quote
    launcher.write_text("#!/bin/sh\n" + f"HOME={quote(str(owner))} "
                        f"PATH={quote(str(owner / '.local/bin') + ':/usr/bin:/bin:/usr/sbin:/sbin')} "
                        f"exec {quote(str(driver))} --state-dir {quote(str(state))} \"$@\"\n")
    launcher.chmod(0o755)


def live(folder: Path, *, owner: Path | None = None) -> int:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("metadata", "unit", "live"))
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
        program_policy(folder, value)
        runtime_probe(folder)
        status = live(folder) if args.mode == "live" else unit(folder)
        verify(folder, candidate=args.candidate is not None)
        return status
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"Cannot check {COMPONENT}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

# Archived complete imports; restore needed names in their original scope, not at this file tail.
