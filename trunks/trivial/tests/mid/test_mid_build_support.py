
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_build_support.py::BuildMetadata.test_the_project_pin_and_both_locked_psycopg_distributions_agree
# Reason: Metadata/version/default/refusal tables restate readable packaging validation. Case reviewed: The project pin and both locked psycopg distributions agree.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_build_support.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_project_pin_and_both_locked_psycopg_distributions_agree(self) -> None:
#         version, pin, psycopg = metadata(self.source)
#         self.assertEqual((version, pin["version"], psycopg), ("1.0.0", "3.14.8", "3.3.6"))
#         (self.source / "package.json").write_text('{"version":"wrong"}')
#         with self.assertRaisesRegex(ValueError, "metadata"):
#             metadata(self.source)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_build_support.py::BuildMetadata.test_a_different_interpreter_or_an_extra_dependency_is_refused
# Reason: Metadata/version/default/refusal tables restate readable packaging validation. Case reviewed: A different interpreter or an extra dependency is refused.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_build_support.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_different_interpreter_or_an_extra_dependency_is_refused(self) -> None:
#         project = self.source / "pyproject.toml"
#         original = project.read_text()
#         for value in (original.replace("==3.14.8", ">=3.14"),
#                       original.replace('dependencies = [', 'dependencies = ["requests", ')):
#             with self.subTest(project=value):
#                 project.write_text(value)
#                 with self.assertRaises(ValueError):
#                     metadata(self.source)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_build_support.py::BuildMetadata.test_a_candidate_is_zero_and_cannot_replace_a_numbered_build
# Reason: Metadata/version/default/refusal tables restate readable packaging validation. Case reviewed: A candidate is zero and cannot replace a numbered build.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_build_support.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_candidate_is_zero_and_cannot_replace_a_numbered_build(self) -> None:
#         self.assertEqual(build_folder(str(self.folder), root=self.source), (self.folder, "0"))
#         (self.folder / "build.json").write_text("{}")
#         with self.assertRaisesRegex(ValueError, "candidate"):
#             build_folder(str(self.folder), root=self.source)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_build_support.py::BuildMetadata.test_a_numbered_build_must_match_all_of_its_metadata
# Reason: Metadata/version/default/refusal tables restate readable packaging validation. Case reviewed: A numbered build must match all of its metadata.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_build_support.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_numbered_build_must_match_all_of_its_metadata(self) -> None:
#         record = {"component": COMPONENT, "entry": ENTRY, "build": "a", "packageVersion": "1.0.0", "rootContracts": [1]}
#         with mock.patch.dict("os.environ", {"ARBOL_BUILD_DIR": str(self.folder), "ARBOL_BUILD_NUMBER": "a"}):
#             (self.folder / "build.json").write_text(json.dumps(record))
#             self.assertEqual(build_folder(root=self.source), (self.folder, "a"))
#             for key, value in (("build", "b"), ("component", "other"), ("entry", "../outside"),
#                                ("packageVersion", "2"), ("rootContracts", [2])):
#                 with self.subTest(key=key):
#                     (self.folder / "build.json").write_text(json.dumps({**record, key: value}))
#                     with self.assertRaises(ValueError):
#                         build_folder(root=self.source)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_build_support.py::BuildMetadata.test_the_target_is_explicit_and_unsupported_architectures_are_refused
# Reason: Metadata/version/default/refusal tables restate readable packaging validation. Case reviewed: The target is explicit and unsupported architectures are refused.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_build_support.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_target_is_explicit_and_unsupported_architectures_are_refused(self) -> None:
#         with mock.patch("platform.machine", return_value="arm64"):
#             self.assertEqual(target(), "aarch64-apple-darwin")
#         with mock.patch("platform.machine", return_value="unknown"), self.assertRaises(ValueError):
#             target()
# LOW-TIER-SOURCE-END
# LOW-TIER-END
