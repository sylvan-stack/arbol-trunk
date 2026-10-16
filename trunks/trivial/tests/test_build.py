import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from arbol_trunk_trivial import NAME
from arbol_trunk_trivial.build import BuildRecordError, build_number

TRUNK = Path(__file__).resolve().parents[1]


class BuildNumber(unittest.TestCase):
    def test_outside_a_build_the_build_number_is_0(self) -> None:
        self.assertEqual(build_number(), "0")

    def test_inside_a_build_it_is_read_from_the_record_in_its_own_folder(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            build = Path(folder) / "builds" / "arbol-trunk" / "trivial" / "4"
            package = build / "app" / "arbol_trunk_trivial"
            package.mkdir(parents=True)
            (build / "build.json").write_text(json.dumps({"component": NAME, "build": "4"}), encoding="utf-8")
            self.assertEqual(build_number(package), "4")

    def test_a_record_of_another_component_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "build.json").write_text(json.dumps({"component": "arbol-classifier", "build": "4"}),
                                                     encoding="utf-8")
            with self.assertRaises(BuildRecordError):
                build_number(Path(folder))


class CheckoutScript(unittest.TestCase):
    def test_it_replaces_itself_with_the_folders_own_python_on_entry_py(self) -> None:
        script = TRUNK / "bin" / "arbol-trunk-trivial"
        self.assertTrue(os.access(script, os.X_OK))
        self.assertIn('exec "$root/.venv/bin/python" -I -B "$root/bin/entry.py" "$@"', script.read_text())
        completed = subprocess.run([str(script), "--root", "rct", "settle"], capture_output=True, text=True,
                                   env={"HOME": tempfile.gettempdir(), "PATH": "/usr/bin:/bin"}, timeout=30)
        self.assertEqual(completed.returncode, 1)
        self.assertIn('"error"', completed.stdout)


if __name__ == "__main__":
    unittest.main()
