import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from arbol_trunk_steady.cli import entry  # noqa: E402

entry()
