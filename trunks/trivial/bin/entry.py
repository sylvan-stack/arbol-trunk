import sys
from pathlib import Path

component = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(component / "src"))
if (component.parent / "installation_paths.py").is_file() and component.parent.name == "trunks":
    sys.path.insert(1, str(component.parent))
from arbol_trunk_trivial.cli import entry  # noqa: E402

entry()
