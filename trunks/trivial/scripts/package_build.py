"""Package the Trivial Trunk and its checksum-pinned standalone interpreter (TRV-D20)."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.build_support import (  # noqa: E402
    COMPONENT,
    ENTRY,
    ROOT,
    build_folder,
    digest,
    metadata,
    source_provenance,
    target,
)

ARCHIVE_URL = "https://github.com/astral-sh/python-build-standalone/releases/download/"
MUTABLE = {"build.json", "build.log", "package-manifest.json"}


def archive(distribution: dict[str, Any]) -> Path:
    checksum, url = distribution.get("sha256"), distribution.get("url")
    if (not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum)
            or not isinstance(url, str) or not url.startswith(ARCHIVE_URL)):
        raise ValueError("The Python archive needs an official pinned URL and SHA-256.")
    cache = Path(os.environ.get("ARBOL_PYTHON_ARCHIVE_CACHE", str(Path.home() / ".cache/arbol-driver-build/python")))
    cache.mkdir(parents=True, exist_ok=True)
    saved = cache / (checksum + ".tar.gz")
    if saved.exists():
        if digest(saved) != checksum:
            raise ValueError("The cached Python archive does not match its SHA-256.")
        return saved
    descriptor, name = tempfile.mkstemp(prefix="python-", suffix=".tar.gz", dir=cache)
    os.close(descriptor)
    temporary = Path(name)
    try:
        with urllib.request.urlopen(url, timeout=60) as response, temporary.open("wb") as stream:
            shutil.copyfileobj(response, stream)
        if digest(temporary) != checksum:
            raise ValueError("The downloaded Python archive does not match its SHA-256.")
        temporary.replace(saved)
    finally:
        temporary.unlink(missing_ok=True)
    return saved


def file_digests(folder: Path) -> dict[str, str]:
    return {str(path.relative_to(folder)): digest(path) for path in sorted(folder.rglob("*"))
            if path.is_file() and str(path.relative_to(folder)) not in MUTABLE}


def package(candidate: str | None = None, *, root: Path = ROOT) -> Path:
    folder, number = build_folder(candidate, root=root)
    root = root.resolve()
    if folder == root or folder in root.parents or root in folder.parents:
        raise ValueError("The package cannot overlap its source.")
    if root.parts[-2:] != ("trunks", "trivial"):
        raise ValueError("The component's source must be in trunks/trivial.")
    allowed = set() if candidate is not None else {"build.json", "build.log"}
    if any(path.name not in allowed for path in folder.iterdir()):
        raise ValueError("The new package folder already holds files.")
    version, pin, psycopg = metadata(root)
    architecture = target()
    distribution = pin["distributions"][architecture]
    compressed = archive(distribution)
    runtime = folder / "runtime"
    runtime.mkdir(mode=0o700)
    with tarfile.open(compressed, "r:gz") as bundle:
        bundle.extractall(runtime, filter="data")
    interpreter = runtime / "python/bin/python3.14"
    result = subprocess.run([str(interpreter), "-I", "-B", "-c", "import platform; print(platform.python_version())"],
                            check=True, capture_output=True, text=True, cwd=folder)
    if result.stdout.strip() != pin["version"]:
        raise ValueError("The unpacked interpreter has the wrong version.")
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
    for name in ("src", "tests", "scripts", "bin"):
        shutil.copytree(root / name, folder / name, ignore=ignore)
    for name in ("package.json", "pyproject.toml", ".python-version", "uv.lock", "arbol-build.json", "README.md"):
        shutil.copy2(root / name, folder / name)
    manifest = {"format": 1, "component": COMPONENT, "packageVersion": version, "entry": ENTRY,
                "build": number, "candidate": candidate is not None, "rootContracts": [1],
                "source": source_provenance(root),
                "python": {"version": pin["version"], "target": architecture, "provider": pin["provider"],
                           "release": pin["release"], "archiveUrl": distribution["url"],
                           "archiveSha256": distribution["sha256"], "executable": "runtime/python/bin/python3.14",
                           "executableSha256": digest(interpreter)},
                "dependencies": {"psycopg": psycopg, "psycopg-binary": psycopg}, "files": file_digests(folder)}
    (folder / "package-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return folder


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", help="Absolute empty development folder, outside the registry")
    args = parser.parse_args()
    try:
        folder = package(args.candidate)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, tarfile.TarError) as error:
        print(f"Cannot package {COMPONENT}: {error}", file=sys.stderr)
        return 1
    print(f"Packaged {COMPONENT} in {folder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
