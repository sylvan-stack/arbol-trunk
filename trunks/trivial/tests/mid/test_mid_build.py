
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_build.py::BuildNumber.test_outside_a_build_the_build_number_is_0
# Reason: Build-number dictionaries and checkout launcher duplication add no distinct evidence beyond retained relocated packaged launcher and release gates. Case reviewed: Outside a build the build number is 0.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_outside_a_build_the_build_number_is_0(self) -> None:
#         with tempfile.TemporaryDirectory() as folder:
#             checkout = Path(folder)
#             (checkout / "pyproject.toml").write_text('[project]\nname = "arbol-trunk-trivial"\n')
#             self.assertEqual(build_number(checkout), "0")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_build.py::BuildNumber.test_inside_a_build_it_is_read_from_the_record_in_its_own_folder
# Reason: Build-number dictionaries and checkout launcher duplication add no distinct evidence beyond retained relocated packaged launcher and release gates. Case reviewed: Inside a build it is read from the record in its own folder.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_inside_a_build_it_is_read_from_the_record_in_its_own_folder(self) -> None:
#         with tempfile.TemporaryDirectory() as folder:
#             build = Path(folder) / "builds" / "arbol-trunk" / "trivial" / "4"
#             package = build / "app" / "arbol_trunk_trivial"
#             package.mkdir(parents=True)
#             (build / "build.json").write_text(json.dumps({"component": NAME, "build": "4"}), encoding="utf-8")
#             self.assertEqual(build_number(package), "4")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_build.py::BuildNumber.test_a_record_of_another_component_is_refused
# Reason: Build-number dictionaries and checkout launcher duplication add no distinct evidence beyond retained relocated packaged launcher and release gates. Case reviewed: A record of another component is refused.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_record_of_another_component_is_refused(self) -> None:
#         with tempfile.TemporaryDirectory() as folder:
#             (Path(folder) / "build.json").write_text(json.dumps({"component": "arbol-classifier", "build": "4"}),
#                                                      encoding="utf-8")
#             with self.assertRaises(BuildRecordError):
#                 build_number(Path(folder))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_build.py::CheckoutScript.test_it_replaces_itself_with_the_folders_own_python_on_entry_py
# Reason: Build-number dictionaries and checkout launcher duplication add no distinct evidence beyond retained relocated packaged launcher and release gates. Case reviewed: It replaces itself with the folders own python on entry py.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_it_replaces_itself_with_the_folders_own_python_on_entry_py(self) -> None:
#         script = TRUNK / "bin" / "arbol-trunk-trivial"
#         self.assertTrue(os.access(script, os.X_OK))
#         with tempfile.TemporaryDirectory() as temporary:
#             checkout = Path(temporary).resolve()
#             (checkout / "bin").mkdir()
#             (checkout / ".venv/bin").mkdir(parents=True)
#             entry = checkout / "bin/arbol-trunk-trivial"
#             shutil.copy2(script, entry)
#             interpreter = checkout / ".venv/bin/python"
#             interpreter.write_text("#!/bin/sh\nprintf '%s\\n' \"$$\" \"$@\" > \"$CHECKOUT_ENTRY_REPORT\"\n")
#             interpreter.chmod(0o755)
#             report = checkout / "report"
#             child = subprocess.Popen([str(entry), "two words", ""], env={"CHECKOUT_ENTRY_REPORT": str(report)})
#             self.assertEqual(child.wait(timeout=10), 0)
#             self.assertEqual(report.read_text().splitlines(),
#                              [str(child.pid), "-I", "-B", str(checkout / "bin/entry.py"), "two words", ""])
#             (checkout / "package-manifest.json").write_text("{}")
#             report.unlink()
#             broken = subprocess.run([str(entry)], capture_output=True, text=True, timeout=10)
#             self.assertEqual(broken.returncode, 1)
#             self.assertIn("missing its interpreter", broken.stderr)
#             self.assertFalse(report.exists())
#         completed = subprocess.run([str(script), "--root", "rct", "settle"], capture_output=True, text=True,
#                                    env={"HOME": tempfile.gettempdir(), "PATH": "/usr/bin:/bin"}, timeout=30)
#         self.assertEqual(completed.returncode, 1)
#         self.assertIn('"error"', completed.stdout)
# LOW-TIER-SOURCE-END
# LOW-TIER-END
