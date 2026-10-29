# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.

from audit import opened_files
from arbol_trunk_trivial.settings import default_driver, settings_file

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


# Archived complete imports; restore needed names in their original scope, not at this file tail.

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/test_start.py::Start.test_the_default_driver_comes_from_the_settings_file
# Reason: Checks the straightforward command-driver-or-settings choice.
# Source: arbol-trunk@0c9701e61fdb0afa33c1b85110395cc049b10497:trunks/trivial/tests/test_start.py
# Retained evidence at review: Route preservation when the default driver is used, malformed settings and actual startup integration remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_default_driver_comes_from_the_settings_file(self) -> None:
#         write(settings_file(self.home), {"driver": "codex"})
#         self.assertEqual(self.start().driver, "codex")
#         self.assertEqual(self.start("--driver", "claude").driver, "claude")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/test_start.py::Start.test_no_driver_handed_and_none_in_the_settings_file_is_refused_naming_the_file_and_key
# Reason: Copies the entire static JSON diagnostic for the explicit missing-driver branch.
# Source: arbol-trunk@0c9701e61fdb0afa33c1b85110395cc049b10497:trunks/trivial/tests/test_start.py
# Retained evidence at review: Malformed settings, route preservation and startup failure/integration cases remain; diagnostic prose is not pinned.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_no_driver_handed_and_none_in_the_settings_file_is_refused_naming_the_file_and_key(self) -> None:
#         with self.assertRaises(Refusal) as caught:
#             self.start()
#         self.assertEqual(caught.exception.line(), '{"error":{"code":"invalid_input","message":"No Driver was handed, '
#                                                   'and ~/.arbol/arbol-trunk/trivial.json names none under '
#                                                   '\\"driver\\"."}}')
# LOW-TIER-SOURCE-END
# LOW-TIER-END
