import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from package_fixtures import package_source

from scripts.build_support import digest, read_object, target
from scripts.package_build import archive, copy_dependencies, package


class Packaging(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.source, self.cache = package_source(self.base)
        self.output = self.base / "package"
        self.output.mkdir()
        patch = mock.patch.dict("os.environ", {"ARBOL_PYTHON_ARCHIVE_CACHE": str(self.cache)})
        patch.start()
        self.addCleanup(patch.stop)

    def test_the_package_contains_its_own_runtime_sources_tests_and_file_digests(self) -> None:
        self.assertEqual(package(str(self.output), root=self.source), self.output)
        manifest = read_object(self.output / "package-manifest.json")
        self.assertEqual((manifest["build"], manifest["candidate"], manifest["rootContracts"]), ("0", True, [1]))
        for name in ("runtime/python/bin/python3.14", "runtime/python/lib/python3.14/fixture.txt",
                     "src/arbol_trunk_trivial/run.py", "tests/test_loop.py", "scripts/package_build.py", "bin/entry.py"):
            self.assertEqual(manifest["files"][name], digest(self.output / name))
        self.assertEqual(manifest["source"]["componentPath"], "trunks/trivial")
        with self.assertRaisesRegex(ValueError, "already holds"):
            package(str(self.output), root=self.source)

    def test_both_psycopg_packages_and_their_metadata_are_copied_into_the_build(self) -> None:
        package(str(self.output), root=self.source)
        library = self.output / "runtime/python/lib/python3.14/site-packages"
        manifest = read_object(self.output / "package-manifest.json")
        for name in ("psycopg", "psycopg_binary"):
            self.assertTrue((library / name / "__init__.py").is_file())
            self.assertTrue((library / f"{name}-3.3.6.dist-info/METADATA").is_file())
        self.assertTrue(any("psycopg_binary/" in path and path.endswith(".so") for path in manifest["files"]))
        self.assertEqual(manifest["dependencies"], {"psycopg": "3.3.6", "psycopg-binary": "3.3.6"})
        with self.assertRaises(FileNotFoundError):
            copy_dependencies(self.base / "missing", "3.3.6", installed=self.base / "no-installed-packages")

    def test_a_bad_cached_archive_is_refused_without_a_download_or_extraction(self) -> None:
        distribution = read_object(self.source / "scripts/python-distribution.json")["distributions"][target()]
        cached = self.cache / (distribution["sha256"] + ".tar.gz")
        cached.write_bytes(b"damaged")
        with mock.patch("urllib.request.urlopen") as fetch, self.assertRaisesRegex(ValueError, "SHA-256"):
            package(str(self.output), root=self.source)
        fetch.assert_not_called()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_archives_need_an_official_source_and_a_complete_digest(self) -> None:
        for pin in ({"url": "https://unrelated.invalid/python", "sha256": "a" * 64},
                    {"url": "https://github.com/astral-sh/python-build-standalone/releases/download/x", "sha256": "bad"}):
            with self.subTest(pin=pin), self.assertRaises(ValueError):
                archive(pin)

    def test_a_package_cannot_overwrite_the_source_or_a_nonempty_candidate(self) -> None:
        with self.assertRaisesRegex(ValueError, "overlap"):
            package(str(self.source), root=self.source)
        (self.output / "keep.json").write_text(json.dumps({"keep": True}))
        with self.assertRaisesRegex(ValueError, "already holds"):
            package(str(self.output), root=self.source)
        self.assertEqual((self.output / "keep.json").read_text(), '{"keep": true}')
