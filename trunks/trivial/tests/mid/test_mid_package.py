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
