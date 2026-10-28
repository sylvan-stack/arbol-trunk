import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.build_support import ROOT


class BuildMetadata(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.source = Path(temporary.name).resolve() / "trunks/trivial"
        (self.source / "scripts").mkdir(parents=True)
        for name in ("pyproject.toml", "package.json", "uv.lock", ".python-version", "scripts/python-distribution.json"):
            shutil.copy2(ROOT / name, self.source / name)
        self.folder = Path(temporary.name).resolve() / "build"
        self.folder.mkdir()

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_build_support.py::BuildMetadata.test_the_project_pin_and_both_locked_psycopg_distributions_agree
#     def test_the_project_pin_and_both_locked_psycopg_distributions_agree(self) -> None:
#         version, pin, psycopg = metadata(self.source)
#         self.assertEqual((version, pin["version"], psycopg), ("1.0.0", "3.14.8", "3.3.6"))
#         (self.source / "package.json").write_text('{"version":"wrong"}')
#         with self.assertRaisesRegex(ValueError, "metadata"):
#             metadata(self.source)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_build_support.py::BuildMetadata.test_the_project_pin_and_both_locked_psycopg_distributions_agree

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_build_support.py::BuildMetadata.test_a_different_interpreter_or_an_extra_dependency_is_refused
#     def test_a_different_interpreter_or_an_extra_dependency_is_refused(self) -> None:
#         project = self.source / "pyproject.toml"
#         original = project.read_text()
#         for value in (original.replace("==3.14.8", ">=3.14"),
#                       original.replace('dependencies = [', 'dependencies = ["requests", ')):
#             with self.subTest(project=value):
#                 project.write_text(value)
#                 with self.assertRaises(ValueError):
#                     metadata(self.source)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_build_support.py::BuildMetadata.test_a_different_interpreter_or_an_extra_dependency_is_refused

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_build_support.py::BuildMetadata.test_a_candidate_is_zero_and_cannot_replace_a_numbered_build
#     def test_a_candidate_is_zero_and_cannot_replace_a_numbered_build(self) -> None:
#         self.assertEqual(build_folder(str(self.folder), root=self.source), (self.folder, "0"))
#         (self.folder / "build.json").write_text("{}")
#         with self.assertRaisesRegex(ValueError, "candidate"):
#             build_folder(str(self.folder), root=self.source)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_build_support.py::BuildMetadata.test_a_candidate_is_zero_and_cannot_replace_a_numbered_build

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_build_support.py::BuildMetadata.test_a_numbered_build_must_match_all_of_its_metadata
#     def test_a_numbered_build_must_match_all_of_its_metadata(self) -> None:
#         record = {"component": COMPONENT, "entry": ENTRY, "build": "a", "packageVersion": "1.0.0", "rootContracts": [1]}
#         with mock.patch.dict("os.environ", {"ARBOL_BUILD_DIR": str(self.folder), "ARBOL_BUILD_NUMBER": "a"}):
#             (self.folder / "build.json").write_text(json.dumps(record))
#             self.assertEqual(build_folder(root=self.source), (self.folder, "a"))
#             for key, value in (("build", "b"), ("component", "other"), ("entry", "../outside"),
#                                ("packageVersion", "2"), ("rootContracts", [2])):
#                 with self.subTest(key=key):
#                     (self.folder / "build.json").write_text(json.dumps({**record, key: value}))
#                     with self.assertRaises(ValueError):
#                         build_folder(root=self.source)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_build_support.py::BuildMetadata.test_a_numbered_build_must_match_all_of_its_metadata

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_build_support.py::BuildMetadata.test_the_target_is_explicit_and_unsupported_architectures_are_refused
#     def test_the_target_is_explicit_and_unsupported_architectures_are_refused(self) -> None:
#         with mock.patch("platform.machine", return_value="arm64"):
#             self.assertEqual(target(), "aarch64-apple-darwin")
#         with mock.patch("platform.machine", return_value="unknown"), self.assertRaises(ValueError):
#             target()
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_build_support.py::BuildMetadata.test_the_target_is_explicit_and_unsupported_architectures_are_refused

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_build_support.py:1
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_build_support.py:1
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_build_support.py:6
# from unittest import mock
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_build_support.py:6
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_build_support.py:8
# from scripts.build_support import COMPONENT, ENTRY, ROOT, build_folder, metadata, target
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_build_support.py:8
