
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_check_build.py::PackageChecks.test_the_manifest_is_checked_after_relocation
# Reason: Manifest-field mutations and import/identity tables mostly restate the verifier; actual packaged integrity/runtime qualification remains the release gate. Case reviewed: The manifest is checked after relocation.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_check_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_manifest_is_checked_after_relocation(self) -> None:
#         moved = self.base / "moved"
#         self.folder.rename(moved)
#         self.assertEqual(verify(moved, candidate=True)["build"], "0")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_check_build.py::PackageChecks.test_changed_runtime_or_source_bytes_and_extra_files_are_refused
# Reason: Manifest-field mutations and import/identity tables mostly restate the verifier; actual packaged integrity/runtime qualification remains the release gate. Case reviewed: Changed runtime or source bytes and extra files are refused.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_check_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_changed_runtime_or_source_bytes_and_extra_files_are_refused(self) -> None:
#         for relative in ("src/arbol_trunk_trivial/run.py", "runtime/python/lib/python3.14/fixture.txt"):
#             with self.subTest(path=relative):
#                 path = self.folder / relative
#                 before = path.read_bytes()
#                 path.write_bytes(before + b"\n# changed\n")
#                 with self.assertRaisesRegex(ValueError, "changed"):
#                     verify(self.folder, candidate=True)
#                 path.write_bytes(before)
#         (self.folder / "extra.py").write_text("pass\n")
#         with self.assertRaisesRegex(ValueError, "file set"):
#             verify(self.folder, candidate=True)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_check_build.py::PackageChecks.test_a_numbered_record_is_checked_against_the_package
# Reason: Manifest-field mutations and import/identity tables mostly restate the verifier; actual packaged integrity/runtime qualification remains the release gate. Case reviewed: A numbered record is checked against the package.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_check_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_numbered_record_is_checked_against_the_package(self) -> None:
#         manifest = read_object(self.folder / "package-manifest.json")
#         manifest.update(candidate=False, build="a")
#         (self.folder / "package-manifest.json").write_text(json.dumps(manifest))
#         (self.folder / "build.json").write_text(json.dumps({"component": "arbol-trunk/trivial", "build": "b"}))
#         with self.assertRaisesRegex(ValueError, "record differ"):
#             verify(self.folder, candidate=False)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_check_build.py::PackageChecks.test_a_unit_check_with_no_tests_is_refused
# Reason: Manifest-field mutations and import/identity tables mostly restate the verifier; actual packaged integrity/runtime qualification remains the release gate. Case reviewed: A unit check with no tests is refused.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_check_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_unit_check_with_no_tests_is_refused(self) -> None:
#         empty = self.base / "empty"
#         (empty / "tests").mkdir(parents=True)
#         with self.assertRaisesRegex(ValueError, "no tests"):
#             unit(empty)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_check_build.py::PackageChecks.test_the_packaged_program_has_only_its_allowed_imports
# Reason: Manifest-field mutations and import/identity tables mostly restate the verifier; actual packaged integrity/runtime qualification remains the release gate. Case reviewed: The packaged program has only its allowed imports.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_check_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_packaged_program_has_only_its_allowed_imports(self) -> None:
#         manifest = read_object(self.folder / "package-manifest.json")
#         program_policy(self.folder, manifest)
#         path = self.folder / "src/arbol_trunk_trivial/run.py"
#         path.write_text(path.read_text() + "\nimport requests\n")
#         with self.assertRaisesRegex(ValueError, "imports requests"):
#             program_policy(self.folder, manifest)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_check_build.py::PackageChecks.test_source_from_another_trunk_is_refused
# Reason: Manifest-field mutations and import/identity tables mostly restate the verifier; actual packaged integrity/runtime qualification remains the release gate. Case reviewed: Source from another trunk is refused.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_check_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_source_from_another_trunk_is_refused(self) -> None:
#         manifest = read_object(self.folder / "package-manifest.json")
#         manifest["source"]["componentPath"] = "trunks/another"
#         with self.assertRaisesRegex(ValueError, "trunks/trivial"):
#             program_policy(self.folder, manifest)
#         manifest["source"]["componentPath"] = "trunks/trivial"
#         (self.folder / "src/another_trunk").mkdir()
#         with self.assertRaisesRegex(ValueError, "only the Trivial Trunk"):
#             program_policy(self.folder, manifest)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_check_build.py::PackageChecks.test_a_different_program_identity_or_contract_version_is_refused
# Reason: Manifest-field mutations and import/identity tables mostly restate the verifier; actual packaged integrity/runtime qualification remains the release gate. Case reviewed: A different program identity or contract version is refused.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_check_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_different_program_identity_or_contract_version_is_refused(self) -> None:
#         manifest = read_object(self.folder / "package-manifest.json")
#         path = self.folder / "src/arbol_trunk_trivial/__init__.py"
#         original = path.read_text()
#         path.write_text(original.replace('CODE_NAME = "trivial"', 'CODE_NAME = "another"'))
#         with self.assertRaisesRegex(ValueError, "code name"):
#             program_policy(self.folder, manifest)
#         path.write_text(original)
#         path = self.folder / "src/arbol_trunk_trivial/root.py"
#         path.write_text(path.read_text().replace("ROOT_CONTRACTS = (1,)", "ROOT_CONTRACTS = (2,)"))
#         with self.assertRaisesRegex(ValueError, "Root Contracts"):
#             program_policy(self.folder, manifest)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_check_build.py::PackageChecks.test_a_different_build_description_is_refused
# Reason: Manifest-field mutations and import/identity tables mostly restate the verifier; actual packaged integrity/runtime qualification remains the release gate. Case reviewed: A different build description is refused.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_check_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_different_build_description_is_refused(self) -> None:
#         description = read_object(self.folder / "arbol-build.json")
#         description["rootContracts"] = [2]
#         (self.folder / "arbol-build.json").write_text(json.dumps(description))
#         with self.assertRaisesRegex(ValueError, "Build description"):
#             program_policy(self.folder, read_object(self.folder / "package-manifest.json"))
# LOW-TIER-SOURCE-END
# LOW-TIER-END
