"""Private canonical installation used by the Trivial Build's live gate."""

from __future__ import annotations

import importlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any


def working_build(variable: str, component: str, entry: str) -> tuple[Path, str]:
    raw = os.environ.get(variable, "")
    if not raw or not Path(raw).is_absolute():
        raise ValueError(f"{variable} must name an absolute working Build folder for {component}.")
    folder = Path(raw).resolve(strict=True)
    record = json.loads((folder / "build.json").read_text())
    if not isinstance(record, dict):
        raise ValueError(f"{variable} has no Build record.")
    number = record.get("build")
    checks = record.get("checks")
    if (record.get("component") != component or record.get("entry") != entry or record.get("status") != "working"
            or record.get("prunedAt") or not isinstance(number, str) or not re.fullmatch(r"[1-9a-f][0-9a-f]*", number)
            or not isinstance(checks, list) or not checks
            or any(not isinstance(check, dict) or check.get("passed") is not True for check in checks)
            or not (folder / entry).resolve(strict=True).is_relative_to(folder) or not os.access(folder / entry, os.X_OK)):
        raise ValueError(f"{variable} does not name a runnable working {component} Build.")
    manifest = json.loads((folder / "package-manifest.json").read_text())
    if not isinstance(manifest, dict) or any(manifest.get(key) != record.get(key) for key in ("component", "entry", "build")):
        raise ValueError(f"{variable} package identity differs from the selected registry record.")
    return folder, number


class LiveInstallation:
    def __init__(self, arbol: Path) -> None:
        manifest = arbol / "database/migrations.toml"
        schema = tomllib.loads(manifest.read_text())["migrations"]
        names = [entry["file"] for entry in schema]
        if any(not isinstance(name, str) or Path(name).name != name or name in {"", ".", ".."} for name in names):
            raise ValueError("The canonical manifest names a path outside its package.")
        # Verify the Arbol image with its own interpreter before importing fixture support.
        bootstrap = ("import sys; from pathlib import Path; root = Path(sys.argv[1]); "
                     "sys.path.insert(0, str(root / 'scripts')); from backend_package import verify; verify(root)")
        subprocess.run([str(arbol / "runtime/python/bin/python3.14"), "-I", "-B", "-c", bootstrap, str(arbol)],
                       check=True, capture_output=True, timeout=60)
        paths = [str(arbol / relative) for relative in ("tests", "src")]
        sys.path[:0] = paths
        try:
            module = importlib.import_module("backend.support")
            if module.__file__ is None or Path(module.__file__).resolve() != arbol / "tests/backend/support.py":
                raise ValueError("The private backend fixture was loaded from a different Build.")
            self.fixture = module.SingleInstallation(arbol)
            try:
                self.fixture.open_admission()
            except BaseException:
                self.fixture.close()
                raise
        finally:
            for path in paths:
                sys.path.remove(path)
        try:
            place = self.bin / ".arbol-builds/schema"
            place.mkdir(parents=True, mode=0o700)
            for name in ("migrations.toml", *names):
                shutil.copy2(arbol / "database" / name, place / name)
        except BaseException:
            self.close()
            raise

    @property
    def bin(self) -> Path:
        return Path(self.fixture.bin)

    def run(self, entry: Path, subscription: str) -> tuple[int, str]:
        env = {**self.fixture.env, "ARBOL_EXCHANGE_RUNTIME_DIR": str(self.fixture.runtime),
               "ARBOL_EXCHANGE_BIN_DIR": str(self.bin)}
        for key in ("ARBOL_TEST_TIME_SCALE", "ARBOL_EXCHANGE_ADMISSION_GENERATION", "ARBOL_ROOT", "ARBOL_CHAT"):
            env.pop(key, None)
        args = [str(entry), "run", "--driver", "claude", "--subscription", subscription, "--model", "haiku",
                "Answer with the single word: ready"]
        with subprocess.Popen(args, cwd=self.fixture.work, env=env, start_new_session=True, stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as child:
            try:
                output, _ = child.communicate(timeout=300)
            except subprocess.TimeoutExpired:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                child.communicate(timeout=10)
                raise
            return child.returncode, output

    def rows(self, query: str) -> list[dict[str, Any]]:
        statement = f"SELECT coalesce(json_agg(row_to_json(rows)), '[]') FROM ({query}) rows"
        result: list[dict[str, Any]] = json.loads(self.fixture.cluster.sql(statement.encode()))
        return result

    def close(self) -> None:
        self.fixture.close()
