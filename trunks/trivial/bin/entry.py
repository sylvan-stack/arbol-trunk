import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from arbol_trunk_trivial.cli import entry  # noqa: E402

entry()
