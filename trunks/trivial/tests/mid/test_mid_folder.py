
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_folder.py::Folder.test_it_is_made_whole_with_its_three_files_and_the_modes_0700_and_0600
# Reason: Folder names/modes/field copies and process date formatting mostly restate implementation; real claim coordination and contract recovery exercise the consequential boundary. Case reviewed: It is made whole with its three files and the modes 0700 and 0600.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_folder.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_folder.py::Folder.test_a_folder_of_either_name_there_already_is_in_progress_and_what_was_made_is_removed
# Reason: Folder names/modes/field copies and process date formatting mostly restate implementation; real claim coordination and contract recovery exercise the consequential boundary. Case reviewed: A folder of either name there already is in progress and what was made is removed.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_folder.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_folder.py::Folder.test_the_record_is_replaced_whole_and_who_runs_it_never_changes
# Reason: Folder names/modes/field copies and process date formatting mostly restate implementation; real claim coordination and contract recovery exercise the consequential boundary. Case reviewed: The record is replaced whole and who runs it never changes.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_folder.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_folder.py::Folder.test_it_goes_by_way_of_its_old_name
# Reason: Folder names/modes/field copies and process date formatting mostly restate implementation; real claim coordination and contract recovery exercise the consequential boundary. Case reviewed: It goes by way of its old name.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_folder.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_it_goes_by_way_of_its_old_name(self) -> None:
#         folder = ExchangeFolder.make(self.exchanges, EXCHANGE, RECORD)
#         folder.remove()
#         self.assertEqual(os.listdir(self.exchanges), [])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_folder.py::Process.test_its_start_is_the_time_ps_gives_in_utc
# Reason: Folder names/modes/field copies and process date formatting mostly restate implementation; real claim coordination and contract recovery exercise the consequential boundary. Case reviewed: Its start is the time ps gives in utc.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_folder.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_its_start_is_the_time_ps_gives_in_utc(self) -> None:
#         started = datetime.strptime(started_at(), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
#         self.assertLess(abs(started.timestamp() - time.time()), 600)
#         self.assertRegex(started_at(), r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.000Z$")
# LOW-TIER-SOURCE-END
# LOW-TIER-END
