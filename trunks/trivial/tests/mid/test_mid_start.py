"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_start as _support
# from test_start import (
#     Path,
#     Prepared,
#     Start,
#     handed,
#     json,
#     os,
#     parse,
#     prepare,
#     roots_folder,
#     security_stand_in,
#     tempfile,
#     unittest,
#     write,
# )


# class Start(_support.Start):
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


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_start.py:7
# from audit import opened_files
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_start.py:7

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_start.py:12
# from arbol_trunk_trivial.settings import default_driver, settings_file
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_start.py:12

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
