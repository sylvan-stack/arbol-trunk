import tempfile
import unittest
from pathlib import Path
from unittest import mock

from package_fixtures import package_source

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

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_check_build.py::PackageChecks.test_the_manifest_is_checked_after_relocation
#     def test_the_manifest_is_checked_after_relocation(self) -> None:
#         moved = self.base / "moved"
#         self.folder.rename(moved)
#         self.assertEqual(verify(moved, candidate=True)["build"], "0")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_check_build.py::PackageChecks.test_the_manifest_is_checked_after_relocation

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_check_build.py::PackageChecks.test_changed_runtime_or_source_bytes_and_extra_files_are_refused
#     def test_changed_runtime_or_source_bytes_and_extra_files_are_refused(self) -> None:
#         for relative in ("src/arbol_trunk_trivial/run.py", "runtime/python/lib/python3.14/fixture.txt"):
#             with self.subTest(path=relative):
#                 path = self.folder / relative
#                 before = path.read_bytes()
#                 path.write_bytes(before + b"\n# changed\n")
#                 with self.assertRaisesRegex(ValueError, "changed"):
#                     verify(self.folder, candidate=True)
#                 path.write_bytes(before)
#         (self.folder / "extra.py").write_text("pass\n")
#         with self.assertRaisesRegex(ValueError, "file set"):
#             verify(self.folder, candidate=True)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_check_build.py::PackageChecks.test_changed_runtime_or_source_bytes_and_extra_files_are_refused

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_check_build.py::PackageChecks.test_a_numbered_record_is_checked_against_the_package
#     def test_a_numbered_record_is_checked_against_the_package(self) -> None:
#         manifest = read_object(self.folder / "package-manifest.json")
#         manifest.update(candidate=False, build="a")
#         (self.folder / "package-manifest.json").write_text(json.dumps(manifest))
#         (self.folder / "build.json").write_text(json.dumps({"component": "arbol-trunk/trivial", "build": "b"}))
#         with self.assertRaisesRegex(ValueError, "record differ"):
#             verify(self.folder, candidate=False)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_check_build.py::PackageChecks.test_a_numbered_record_is_checked_against_the_package

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_check_build.py::PackageChecks.test_a_unit_check_with_no_tests_is_refused
#     def test_a_unit_check_with_no_tests_is_refused(self) -> None:
#         empty = self.base / "empty"
#         (empty / "tests").mkdir(parents=True)
#         with self.assertRaisesRegex(ValueError, "no tests"):
#             unit(empty)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_check_build.py::PackageChecks.test_a_unit_check_with_no_tests_is_refused

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_check_build.py::PackageChecks.test_the_packaged_program_has_only_its_allowed_imports
#     def test_the_packaged_program_has_only_its_allowed_imports(self) -> None:
#         manifest = read_object(self.folder / "package-manifest.json")
#         program_policy(self.folder, manifest)
#         path = self.folder / "src/arbol_trunk_trivial/run.py"
#         path.write_text(path.read_text() + "\nimport requests\n")
#         with self.assertRaisesRegex(ValueError, "imports requests"):
#             program_policy(self.folder, manifest)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_check_build.py::PackageChecks.test_the_packaged_program_has_only_its_allowed_imports

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_check_build.py::PackageChecks.test_source_from_another_trunk_is_refused
#     def test_source_from_another_trunk_is_refused(self) -> None:
#         manifest = read_object(self.folder / "package-manifest.json")
#         manifest["source"]["componentPath"] = "trunks/another"
#         with self.assertRaisesRegex(ValueError, "trunks/trivial"):
#             program_policy(self.folder, manifest)
#         manifest["source"]["componentPath"] = "trunks/trivial"
#         (self.folder / "src/another_trunk").mkdir()
#         with self.assertRaisesRegex(ValueError, "only the Trivial Trunk"):
#             program_policy(self.folder, manifest)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_check_build.py::PackageChecks.test_source_from_another_trunk_is_refused

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_check_build.py::PackageChecks.test_a_different_program_identity_or_contract_version_is_refused
#     def test_a_different_program_identity_or_contract_version_is_refused(self) -> None:
#         manifest = read_object(self.folder / "package-manifest.json")
#         path = self.folder / "src/arbol_trunk_trivial/__init__.py"
#         original = path.read_text()
#         path.write_text(original.replace('CODE_NAME = "trivial"', 'CODE_NAME = "another"'))
#         with self.assertRaisesRegex(ValueError, "code name"):
#             program_policy(self.folder, manifest)
#         path.write_text(original)
#         path = self.folder / "src/arbol_trunk_trivial/root.py"
#         path.write_text(path.read_text().replace("ROOT_CONTRACTS = (1,)", "ROOT_CONTRACTS = (2,)"))
#         with self.assertRaisesRegex(ValueError, "Root Contracts"):
#             program_policy(self.folder, manifest)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_check_build.py::PackageChecks.test_a_different_program_identity_or_contract_version_is_refused

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_check_build.py::PackageChecks.test_a_different_build_description_is_refused
#     def test_a_different_build_description_is_refused(self) -> None:
#         description = read_object(self.folder / "arbol-build.json")
#         description["rootContracts"] = [2]
#         (self.folder / "arbol-build.json").write_text(json.dumps(description))
#         with self.assertRaisesRegex(ValueError, "Build description"):
#             program_policy(self.folder, read_object(self.folder / "package-manifest.json"))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_check_build.py::PackageChecks.test_a_different_build_description_is_refused

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_check_build.py:1
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_check_build.py:1
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_check_build.py:9
# from scripts.build_support import read_object
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_check_build.py:9
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_check_build.py:10
# from scripts.check_build import program_policy, unit, verify
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_check_build.py:10
