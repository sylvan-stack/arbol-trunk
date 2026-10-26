import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from package_fixtures import package_source

from scripts.build_support import read_object
from scripts.check_build import unit, verify
from scripts.package_build import package


class PackageChecks(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.source, cache = package_source(self.base)
        self.folder = self.base / "build"
        self.folder.mkdir()
        with mock.patch.dict("os.environ", {"ARBOL_PYTHON_ARCHIVE_CACHE": str(cache)}):
            package(str(self.folder), root=self.source)

    def test_the_manifest_is_checked_after_relocation(self) -> None:
        moved = self.base / "moved"
        self.folder.rename(moved)
        self.assertEqual(verify(moved, candidate=True)["build"], "0")

    def test_changed_runtime_or_source_bytes_and_extra_files_are_refused(self) -> None:
        for relative in ("src/arbol_trunk_trivial/run.py", "runtime/python/lib/python3.14/fixture.txt"):
            with self.subTest(path=relative):
                path = self.folder / relative
                before = path.read_bytes()
                path.write_bytes(before + b"\n# changed\n")
                with self.assertRaisesRegex(ValueError, "changed"):
                    verify(self.folder, candidate=True)
                path.write_bytes(before)
        (self.folder / "extra.py").write_text("pass\n")
        with self.assertRaisesRegex(ValueError, "file set"):
            verify(self.folder, candidate=True)

    def test_a_numbered_record_is_checked_against_the_package(self) -> None:
        manifest = read_object(self.folder / "package-manifest.json")
        manifest.update(candidate=False, build="a")
        (self.folder / "package-manifest.json").write_text(json.dumps(manifest))
        (self.folder / "build.json").write_text(json.dumps({"component": "arbol-trunk/trivial", "build": "b"}))
        with self.assertRaisesRegex(ValueError, "record differ"):
            verify(self.folder, candidate=False)

    def test_a_unit_check_with_no_tests_is_refused(self) -> None:
        empty = self.base / "empty"
        (empty / "tests").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "no tests"):
            unit(empty)
