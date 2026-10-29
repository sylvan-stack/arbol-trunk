
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_start.py::Start.test_a_settings_file_without_a_string_driver_counts_as_none
# Reason: Settings defaults/field copies and open-call counts duplicate full contract launch behavior. Case reviewed: A settings file without a string driver counts as none.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_start.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_settings_file_without_a_string_driver_counts_as_none(self) -> None:
#         for content in (None, "{", {"driver": 1}, ["claude"], {"Driver": "claude"}):
#             with self.subTest(content=content):
#                 if content is not None:
#                     write(settings_file(self.home), content)
#                 self.assertIsNone(default_driver(self.home))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_start.py::Start.test_the_route_stays_as_handed_when_the_driver_comes_from_the_settings_file
# Reason: Settings defaults/field copies and open-call counts duplicate full contract launch behavior. Case reviewed: The route stays as handed when the driver comes from the settings file.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_start.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_route_stays_as_handed_when_the_driver_comes_from_the_settings_file(self) -> None:
#         write(settings_file(self.home), {"driver": "claude"})
#         prepared = self.start("--model", "haiku")
#         self.assertEqual(prepared.handed.route, {"model": "haiku"})
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_start.py::Start.test_a_start_reads_no_settings_file_but_its_own
# Reason: Settings defaults/field copies and open-call counts duplicate full contract launch behavior. Case reviewed: A start reads no settings file but its own.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_start.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_start_reads_no_settings_file_but_its_own(self) -> None:
#         write(settings_file(self.home), {"driver": "claude"})
#         write(self.home / ".arbol" / "arbol-claude-driver.json", {"defaultSubscription": "anthropic"})
#         with opened_files() as files:
#             self.start()
#         under_home = sorted({os.path.relpath(file, self.home) for file in files
#                              if os.path.realpath(file).startswith(str(self.home))})
#         self.assertEqual(under_home, [".arbol/arbol-trunk/trivial.json", ".arbol/database.json",
#                                       "Library/Application Support/Arbol/roots/rct/root.json"])
# LOW-TIER-SOURCE-END
# LOW-TIER-END
