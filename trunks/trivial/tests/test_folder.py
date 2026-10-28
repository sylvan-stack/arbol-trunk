import os
import stat
import tempfile
import unittest
from pathlib import Path

EXCHANGE = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
RECORD = {"rootContract": 1, "root": "rct", "exchange": EXCHANGE, "chat": "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b",
          "trunk": "trivial", "build": "0", "process": {"pid": 1, "startedAt": "2026-10-15T09:30:00.000Z"},
          "route": {}, "workingFolder": "/tmp",
          "signsOfLife": {"heartbeat": 0, "waitingFor": "database", "since": "2026-10-15T09:30:00.000Z"}}


def mode(path: Path) -> int:
    return stat.S_IMODE(os.stat(path).st_mode)


class Folder(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.exchanges = Path(folder.name)
        os.umask(0o022)

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_folder.py::Folder.test_it_is_made_whole_with_its_three_files_and_the_modes_0700_and_0600
#     def test_it_is_made_whole_with_its_three_files_and_the_modes_0700_and_0600(self) -> None:
#         folder = ExchangeFolder.make(self.exchanges, EXCHANGE, RECORD)
#         self.assertEqual(sorted(os.listdir(self.exchanges)), [EXCHANGE])
#         self.assertEqual(sorted(os.listdir(folder.path)), ["control", "events.jsonl", "record.json"])
#         self.assertEqual(mode(folder.path), 0o700)
#         for name in ("control", "events.jsonl", "record.json"):
#             self.assertEqual(mode(folder.path / name), 0o600)
#         self.assertEqual(json.loads((folder.path / "record.json").read_text()), RECORD)
#         self.assertNotIn("acceptedAt", RECORD)
#         self.assertEqual((folder.path / "events.jsonl").read_bytes(), b"")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_folder.py::Folder.test_it_is_made_whole_with_its_three_files_and_the_modes_0700_and_0600

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_folder.py::Folder.test_a_folder_of_either_name_there_already_is_in_progress_and_what_was_made_is_removed
#     def test_a_folder_of_either_name_there_already_is_in_progress_and_what_was_made_is_removed(self) -> None:
#         for name in (EXCHANGE, f".{EXCHANGE}.new"):
#             with self.subTest(name=name):
#                 (self.exchanges / name).mkdir()
#                 (self.exchanges / name / "record.json").write_text("{}")
#                 with self.assertRaises(Refusal) as caught:
#                     ExchangeFolder.make(self.exchanges, EXCHANGE, RECORD)
#                 self.assertEqual(caught.exception.code, "in_progress")
#                 self.assertEqual(os.listdir(self.exchanges), [name])
#                 (self.exchanges / name / "record.json").unlink()
#                 (self.exchanges / name).rmdir()
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_folder.py::Folder.test_a_folder_of_either_name_there_already_is_in_progress_and_what_was_made_is_removed

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_folder.py::Folder.test_the_record_is_replaced_whole_and_who_runs_it_never_changes
#     def test_the_record_is_replaced_whole_and_who_runs_it_never_changes(self) -> None:
#         folder = ExchangeFolder.make(self.exchanges, EXCHANGE, RECORD)
#         folder.update(acceptedAt="2026-10-15T09:30:00.412Z")
#         self.assertEqual(json.loads((folder.path / "record.json").read_text()),
#                          {**RECORD, "acceptedAt": "2026-10-15T09:30:00.412Z"})
#         self.assertFalse((folder.path / "record.json.new").exists())
#         self.assertEqual(mode(folder.path / "record.json"), 0o600)
#         for name in ("root", "chat", "route", "process", "workingFolder"):
#             with self.subTest(name=name), self.assertRaises(ValueError):
#                 folder.update(**{name: "other"})
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_folder.py::Folder.test_the_record_is_replaced_whole_and_who_runs_it_never_changes

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_folder.py::Folder.test_it_goes_by_way_of_its_old_name
#     def test_it_goes_by_way_of_its_old_name(self) -> None:
#         folder = ExchangeFolder.make(self.exchanges, EXCHANGE, RECORD)
#         folder.remove()
#         self.assertEqual(os.listdir(self.exchanges), [])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_folder.py::Folder.test_it_goes_by_way_of_its_old_name


class Process(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_folder.py::Process.test_its_start_is_the_time_ps_gives_in_utc
#     def test_its_start_is_the_time_ps_gives_in_utc(self) -> None:
#         started = datetime.strptime(started_at(), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
#         self.assertLess(abs(started.timestamp() - time.time()), 600)
#         self.assertRegex(started_at(), r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.000Z$")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_folder.py::Process.test_its_start_is_the_time_ps_gives_in_utc


if __name__ == "__main__":
    unittest.main()

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_folder.py:1
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_folder.py:1
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_folder.py:5
# import time
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_folder.py:5
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_folder.py:7
# from datetime import UTC, datetime
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_folder.py:7
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_folder.py:10
# from arbol_trunk_trivial.errors import Refusal
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_folder.py:10
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_folder.py:11
# from arbol_trunk_trivial.folder import ExchangeFolder
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_folder.py:11
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_folder.py:12
# from arbol_trunk_trivial.process import started_at
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_folder.py:12
