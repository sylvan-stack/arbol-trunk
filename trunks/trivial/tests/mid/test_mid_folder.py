"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_folder as _support
from test_folder import (
    EXCHANGE,
    ExchangeFolder,
    Folder,
    Path,
    Process,
    RECORD,
    Refusal,
    UTC,
    datetime,
    json,
    mode,
    os,
    started_at,
    stat,
    tempfile,
    time,
    unittest,
)


class Folder(_support.Folder):
# TEST-TIER-BEGIN trunks/trivial/tests/test_folder.py::Folder.test_it_is_made_whole_with_its_three_files_and_the_modes_0700_and_0600
    def test_it_is_made_whole_with_its_three_files_and_the_modes_0700_and_0600(self) -> None:
        folder = ExchangeFolder.make(self.exchanges, EXCHANGE, RECORD)
        self.assertEqual(sorted(os.listdir(self.exchanges)), [EXCHANGE])
        self.assertEqual(sorted(os.listdir(folder.path)), ["control", "events.jsonl", "record.json"])
        self.assertEqual(mode(folder.path), 0o700)
        for name in ("control", "events.jsonl", "record.json"):
            self.assertEqual(mode(folder.path / name), 0o600)
        self.assertEqual(json.loads((folder.path / "record.json").read_text()), RECORD)
        self.assertNotIn("acceptedAt", RECORD)
        self.assertEqual((folder.path / "events.jsonl").read_bytes(), b"")
# TEST-TIER-END trunks/trivial/tests/test_folder.py::Folder.test_it_is_made_whole_with_its_three_files_and_the_modes_0700_and_0600

# TEST-TIER-BEGIN trunks/trivial/tests/test_folder.py::Folder.test_a_folder_of_either_name_there_already_is_in_progress_and_what_was_made_is_removed
    def test_a_folder_of_either_name_there_already_is_in_progress_and_what_was_made_is_removed(self) -> None:
        for name in (EXCHANGE, f".{EXCHANGE}.new"):
            with self.subTest(name=name):
                (self.exchanges / name).mkdir()
                (self.exchanges / name / "record.json").write_text("{}")
                with self.assertRaises(Refusal) as caught:
                    ExchangeFolder.make(self.exchanges, EXCHANGE, RECORD)
                self.assertEqual(caught.exception.code, "in_progress")
                self.assertEqual(os.listdir(self.exchanges), [name])
                (self.exchanges / name / "record.json").unlink()
                (self.exchanges / name).rmdir()
# TEST-TIER-END trunks/trivial/tests/test_folder.py::Folder.test_a_folder_of_either_name_there_already_is_in_progress_and_what_was_made_is_removed

# TEST-TIER-BEGIN trunks/trivial/tests/test_folder.py::Folder.test_the_record_is_replaced_whole_and_who_runs_it_never_changes
    def test_the_record_is_replaced_whole_and_who_runs_it_never_changes(self) -> None:
        folder = ExchangeFolder.make(self.exchanges, EXCHANGE, RECORD)
        folder.update(acceptedAt="2026-10-15T09:30:00.412Z")
        self.assertEqual(json.loads((folder.path / "record.json").read_text()),
                         {**RECORD, "acceptedAt": "2026-10-15T09:30:00.412Z"})
        self.assertFalse((folder.path / "record.json.new").exists())
        self.assertEqual(mode(folder.path / "record.json"), 0o600)
        for name in ("root", "chat", "route", "process", "workingFolder"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                folder.update(**{name: "other"})
# TEST-TIER-END trunks/trivial/tests/test_folder.py::Folder.test_the_record_is_replaced_whole_and_who_runs_it_never_changes

# TEST-TIER-BEGIN trunks/trivial/tests/test_folder.py::Folder.test_it_goes_by_way_of_its_old_name
    def test_it_goes_by_way_of_its_old_name(self) -> None:
        folder = ExchangeFolder.make(self.exchanges, EXCHANGE, RECORD)
        folder.remove()
        self.assertEqual(os.listdir(self.exchanges), [])
# TEST-TIER-END trunks/trivial/tests/test_folder.py::Folder.test_it_goes_by_way_of_its_old_name



class Process(_support.Process):
# TEST-TIER-BEGIN trunks/trivial/tests/test_folder.py::Process.test_its_start_is_the_time_ps_gives_in_utc
    def test_its_start_is_the_time_ps_gives_in_utc(self) -> None:
        started = datetime.strptime(started_at(), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
        self.assertLess(abs(started.timestamp() - time.time()), 600)
        self.assertRegex(started_at(), r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.000Z$")
# TEST-TIER-END trunks/trivial/tests/test_folder.py::Process.test_its_start_is_the_time_ps_gives_in_utc
