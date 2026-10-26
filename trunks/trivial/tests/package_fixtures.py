"""Small, offline package inputs: no download or real interpreter is needed by a unit check."""

from __future__ import annotations

import io
import json
import shutil
import tarfile
from pathlib import Path

from scripts.build_support import ROOT, digest, read_object
from scripts.package_build import ARCHIVE_URL


def package_source(base: Path) -> tuple[Path, Path]:
    source = base / "trunks/trivial"
    source.mkdir(parents=True)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for name in ("src", "scripts", "tests", "bin"):
        shutil.copytree(ROOT / name, source / name, ignore=ignore)
    for name in ("package.json", "pyproject.toml", ".python-version", "uv.lock", "arbol-build.json", "README.md"):
        shutil.copy2(ROOT / name, source / name)
    cache = base / "cache"
    cache.mkdir()
    small = cache / "small.tar.gz"
    with tarfile.open(small, "w:gz") as bundle:
        for name, data in (("python/bin/python3.14", b"#!/bin/sh\nif [ \"$3\" = -c ]; then printf '3.14.8\\n'; exit 0; fi\n"
                            b"if [ \"$3\" = compileall ]; then exit 0; fi\n"
                            b"printf '%s\\n' \"$$\" \"$@\" > \"$PACKAGE_FIXTURE_REPORT\"\n"),
                           ("python/lib/python3.14/fixture.txt", b"runtime file\n")):
            item = tarfile.TarInfo(name)
            item.size, item.mode = len(data), 0o755 if "/bin/" in name else 0o644
            bundle.addfile(item, io.BytesIO(data))
    checksum = digest(small)
    small.rename(cache / (checksum + ".tar.gz"))
    pin = read_object(source / "scripts/python-distribution.json")
    for distribution in pin["distributions"].values():
        distribution["sha256"] = checksum
        distribution["url"] = ARCHIVE_URL + "fixture/python.tar.gz"
    (source / "scripts/python-distribution.json").write_text(json.dumps(pin))
    return source, cache
