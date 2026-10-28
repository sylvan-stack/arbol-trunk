import json
import os
import tempfile
import unittest
from pathlib import Path

from stand_ins import security_stand_in

from arbol_trunk_trivial.command import handed, parse
from arbol_trunk_trivial.root import roots_folder
from arbol_trunk_trivial.start import Prepared, prepare


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")


class Start(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(os.path.realpath(folder.name))
        write(roots_folder(self.home) / "rct" / "root.json", {"database": "arbol_rct", "rootContract": 1})
        write(self.home / ".arbol" / "database.json", {"address": "postgresql://rct@%2Ftmp%2Frct-1a2b"})
        self.security = str(security_stand_in(self.home, status=44))

    def start(self, *args: str) -> Prepared:
        return prepare(handed(parse(["--root", "rct", "run", *args, "hi"]), started_in=str(self.home)), self.home,
                       self.security)


# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_start.py::Start.test_a_settings_file_without_a_string_driver_counts_as_none
#     def test_a_settings_file_without_a_string_driver_counts_as_none(self) -> None:
#         for content in (None, "{", {"driver": 1}, ["claude"], {"Driver": "claude"}):
#             with self.subTest(content=content):
#                 if content is not None:
#                     write(settings_file(self.home), content)
#                 self.assertIsNone(default_driver(self.home))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_start.py::Start.test_a_settings_file_without_a_string_driver_counts_as_none


# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_start.py::Start.test_the_route_stays_as_handed_when_the_driver_comes_from_the_settings_file
#     def test_the_route_stays_as_handed_when_the_driver_comes_from_the_settings_file(self) -> None:
#         write(settings_file(self.home), {"driver": "claude"})
#         prepared = self.start("--model", "haiku")
#         self.assertEqual(prepared.handed.route, {"model": "haiku"})
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_start.py::Start.test_the_route_stays_as_handed_when_the_driver_comes_from_the_settings_file

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_start.py::Start.test_a_start_reads_no_settings_file_but_its_own
#     def test_a_start_reads_no_settings_file_but_its_own(self) -> None:
#         write(settings_file(self.home), {"driver": "claude"})
#         write(self.home / ".arbol" / "arbol-claude-driver.json", {"defaultSubscription": "anthropic"})
#         with opened_files() as files:
#             self.start()
#         under_home = sorted({os.path.relpath(file, self.home) for file in files
#                              if os.path.realpath(file).startswith(str(self.home))})
#         self.assertEqual(under_home, [".arbol/arbol-trunk/trivial.json", ".arbol/database.json",
#                                       "Library/Application Support/Arbol/roots/rct/root.json"])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_start.py::Start.test_a_start_reads_no_settings_file_but_its_own


if __name__ == "__main__":
    unittest.main()

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_start.py:7
# from audit import opened_files
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_start.py:7
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_start.py:12
# from arbol_trunk_trivial.settings import default_driver, settings_file
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_start.py:12
