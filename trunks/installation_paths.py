"""Installation paths shared by the independently packaged Trunks (ARC-5)."""

from pathlib import Path

INSTALLATION_LAYOUT = 2


def installation_root(home: Path | None = None) -> Path:
    return (Path.home() if home is None else home) / ".arbol"


def runtime_folder(home: Path | None = None) -> Path:
    return installation_root(home) / "runtime"
