
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_root.py::TheRoot.test_the_root_json_names_the_database_and_the_version
# Reason: Root/database settings and status maps repeat straightforward branches; retain the whole-start credential timeout instead. Case reviewed: The root json names the database and the version.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_root.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_root_json_names_the_database_and_the_version(self) -> None:
#         write(roots_folder(self.home) / "rct" / "root.json", {"database": "arbol_rct", "rootContract": 1})
#         root = find_root(self.home, "rct")
#         self.assertEqual((root.database, root.root_contract), ("arbol_rct", 1))
#         self.assertEqual(root.exchanges, self.home / "Library/Application Support/Arbol/roots/rct/exchanges")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_root.py::TheRoot.test_a_root_without_a_readable_root_json_is_unknown
# Reason: Root/database settings and status maps repeat straightforward branches; retain the whole-start credential timeout instead. Case reviewed: A root without a readable root json is unknown.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_root.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_root_without_a_readable_root_json_is_unknown(self) -> None:
#         for content in (None, "{", {"rootContract": 1}, [1]):
#             with self.subTest(content=content):
#                 if content is not None:
#                     write(roots_folder(self.home) / "rct" / "root.json", content)
#                 with self.assertRaises(Refusal) as caught:
#                     find_root(self.home, "rct")
#                 self.assertEqual(caught.exception.code, "unknown_root")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_root.py::TheRoot.test_a_version_this_build_does_not_implement_is_a_contract_mismatch
# Reason: Root/database settings and status maps repeat straightforward branches; retain the whole-start credential timeout instead. Case reviewed: A version this build does not implement is a contract mismatch.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_root.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_version_this_build_does_not_implement_is_a_contract_mismatch(self) -> None:
#         write(roots_folder(self.home) / "rct" / "root.json", {"database": "arbol_rct", "rootContract": 2})
#         with self.assertRaises(Refusal) as caught:
#             find_root(self.home, "rct")
#         self.assertEqual(caught.exception.code, "contract_mismatch")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_root.py::TheDatabase.test_the_address_comes_from_database_json_in_the_home_folder
# Reason: Root/database settings and status maps repeat straightforward branches; retain the whole-start credential timeout instead. Case reviewed: The address comes from database json in the home folder.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_root.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_address_comes_from_database_json_in_the_home_folder(self) -> None:
#         write(self.home / ".arbol" / "database.json", {"address": "postgresql://rct@%2Ftmp%2Frct-1a2b"})
#         address = database_address(self.home)
#         self.assertEqual(address, "postgresql://rct@%2Ftmp%2Frct-1a2b")
#         self.assertEqual(role(address), "rct")
#         self.assertEqual(role("postgresql://arbol@127.0.0.1:5432"), "arbol")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_root.py::TheDatabase.test_without_an_address_the_database_is_unavailable
# Reason: Root/database settings and status maps repeat straightforward branches; retain the whole-start credential timeout instead. Case reviewed: Without an address the database is unavailable.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_root.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_without_an_address_the_database_is_unavailable(self) -> None:
#         for content in (None, {"host": "x"}, "nonsense"):
#             with self.subTest(content=content):
#                 if content is not None:
#                     write(self.home / ".arbol" / "database.json", content)
#                 with self.assertRaises(Refusal) as caught:
#                     database_address(self.home)
#                 self.assertEqual(caught.exception.code, "database_unavailable")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_root.py::TheDatabase.test_the_password_is_the_keychain_item_of_the_role
# Reason: Root/database settings and status maps repeat straightforward branches; retain the whole-start credential timeout instead. Case reviewed: The password is the keychain item of the role.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_root.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_password_is_the_keychain_item_of_the_role(self) -> None:
#         security = security_stand_in(self.home, password="pa ss")
#         self.assertEqual(keychain_password("arbol", str(security)), "pa ss")
#         self.assertEqual((self.home / "security.args").read_text(),
#                          "find-generic-password -s com.sylvan-stack.arbol.database -a arbol -w\n")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_root.py::TheDatabase.test_exit_status_44_means_no_item_and_no_password
# Reason: Root/database settings and status maps repeat straightforward branches; retain the whole-start credential timeout instead. Case reviewed: Exit status 44 means no item and no password.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_root.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_exit_status_44_means_no_item_and_no_password(self) -> None:
#         self.assertIsNone(keychain_password("rct", str(security_stand_in(self.home, status=44))))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_root.py::TheDatabase.test_another_failure_or_no_answer_within_2_seconds_is_refused_naming_the_keychain
# Reason: Root/database settings and status maps repeat straightforward branches; retain the whole-start credential timeout instead. Case reviewed: Another failure or no answer within 2 seconds is refused naming the keychain.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_root.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_another_failure_or_no_answer_within_2_seconds_is_refused_naming_the_keychain(self) -> None:
#         for security in (security_stand_in(self.home, status=51), security_stand_in(self.home, sleep=3)):
#             with self.subTest(security=security.read_text()), self.assertRaises(Refusal) as caught:
#                 keychain_password("rct", str(security))
#             self.assertEqual(caught.exception.code, "database_unavailable")
#             self.assertIn("Keychain", caught.exception.message)
# LOW-TIER-SOURCE-END
# LOW-TIER-END
