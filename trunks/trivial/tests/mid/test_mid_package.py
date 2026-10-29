"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_package as _support
from test_package import (mock ,os ,package ,read_object ,subprocess ,target)


class Packaging(_support.Packaging):


# TEST-TIER-BEGIN trunks/trivial/tests/test_package.py::Packaging.test_the_relocated_entry_execs_its_interpreter_and_preserves_arguments_and_pid
    def test_the_relocated_entry_execs_its_interpreter_and_preserves_arguments_and_pid(self) -> None:
        package(str(self.output), root=self.source)
        moved = self.base / "relocated package with spaces"
        self.output.rename(moved)
        report = self.base / "arguments"
        args = ["--root", "two words", "", "run", "-leading-dash"]
        process = subprocess.Popen([str(moved / "bin/arbol-trunk-trivial"), *args],
                                   env={**os.environ, "PACKAGE_FIXTURE_REPORT": str(report)})
        self.assertEqual(process.wait(timeout=10), 0)
        lines = report.read_text().splitlines()
        self.assertEqual(lines, [str(process.pid), "-I", "-B", str(moved / "bin/entry.py"), *args])
# TEST-TIER-END trunks/trivial/tests/test_package.py::Packaging.test_the_relocated_entry_execs_its_interpreter_and_preserves_arguments_and_pid

# TEST-TIER-BEGIN trunks/trivial/tests/test_package.py::Packaging.test_a_bad_cached_archive_is_refused_without_a_download_or_extraction
    def test_a_bad_cached_archive_is_refused_without_a_download_or_extraction(self) -> None:
        distribution = read_object(self.source / "scripts/python-distribution.json")["distributions"][target()]
        cached = self.cache / (distribution["sha256"] + ".tar.gz")
        cached.write_bytes(b"damaged")
        with mock.patch("urllib.request.urlopen") as fetch, self.assertRaisesRegex(ValueError, "SHA-256"):
            package(str(self.output), root=self.source)
        fetch.assert_not_called()
        self.assertEqual(list(self.output.iterdir()), [])
# TEST-TIER-END trunks/trivial/tests/test_package.py::Packaging.test_a_bad_cached_archive_is_refused_without_a_download_or_extraction

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_package.py::Packaging.test_the_package_contains_its_own_runtime_sources_tests_and_file_digests
# Reason: Routine copy/manifest/default/pin tables duplicate implementation and actual qualification; retain executable relocation and corrupt-cache refusal. Case reviewed: The package contains its own runtime sources tests and file digests.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_package.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_package_contains_its_own_runtime_sources_tests_and_file_digests(self) -> None:
#         self.assertEqual(package(str(self.output), root=self.source), self.output)
#         manifest = read_object(self.output / "package-manifest.json")
#         self.assertEqual((manifest["build"], manifest["candidate"], manifest["rootContracts"]), ("0", True, [1]))
#         for name in ("runtime/python/bin/python3.14", "runtime/python/lib/python3.14/fixture.txt",
#                      "src/arbol_trunk_trivial/run.py", "tests/test_loop.py", "scripts/package_build.py", "bin/entry.py"):
#             self.assertEqual(manifest["files"][name], digest(self.output / name))
#         self.assertEqual(manifest["source"]["componentPath"], "trunks/trivial")
#         with self.assertRaisesRegex(ValueError, "already holds"):
#             package(str(self.output), root=self.source)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_package.py::Packaging.test_both_psycopg_packages_and_their_metadata_are_copied_into_the_build
# Reason: Routine copy/manifest/default/pin tables duplicate implementation and actual qualification; retain executable relocation and corrupt-cache refusal. Case reviewed: Both psycopg packages and their metadata are copied into the build.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_package.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_both_psycopg_packages_and_their_metadata_are_copied_into_the_build(self) -> None:
#         package(str(self.output), root=self.source)
#         library = self.output / "runtime/python/lib/python3.14/site-packages"
#         manifest = read_object(self.output / "package-manifest.json")
#         for name in ("psycopg", "psycopg_binary"):
#             self.assertTrue((library / name / "__init__.py").is_file())
#             self.assertTrue((library / f"{name}-3.3.6.dist-info/METADATA").is_file())
#         self.assertTrue(any("psycopg_binary/" in path and path.endswith(".so") for path in manifest["files"]))
#         self.assertEqual(manifest["dependencies"], {"psycopg": "3.3.6", "psycopg-binary": "3.3.6"})
#         with self.assertRaises(FileNotFoundError):
#             copy_dependencies(self.base / "missing", "3.3.6", installed=self.base / "no-installed-packages")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_package.py::Packaging.test_archives_need_an_official_source_and_a_complete_digest
# Reason: Routine copy/manifest/default/pin tables duplicate implementation and actual qualification; retain executable relocation and corrupt-cache refusal. Case reviewed: Archives need an official source and a complete digest.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_package.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_archives_need_an_official_source_and_a_complete_digest(self) -> None:
#         for pin in ({"url": "https://unrelated.invalid/python", "sha256": "a" * 64},
#                     {"url": "https://github.com/astral-sh/python-build-standalone/releases/download/x", "sha256": "bad"}):
#             with self.subTest(pin=pin), self.assertRaises(ValueError):
#                 archive(pin)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_package.py::Packaging.test_a_package_cannot_overwrite_the_source_or_a_nonempty_candidate
# Reason: Routine copy/manifest/default/pin tables duplicate implementation and actual qualification; retain executable relocation and corrupt-cache refusal. Case reviewed: A package cannot overwrite the source or a nonempty candidate.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_package.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_package_cannot_overwrite_the_source_or_a_nonempty_candidate(self) -> None:
#         with self.assertRaisesRegex(ValueError, "overlap"):
#             package(str(self.source), root=self.source)
#         (self.output / "keep.json").write_text(json.dumps({"keep": True}))
#         with self.assertRaisesRegex(ValueError, "already holds"):
#             package(str(self.output), root=self.source)
#         self.assertEqual((self.output / "keep.json").read_text(), '{"keep": true}')
# LOW-TIER-SOURCE-END
# LOW-TIER-END
