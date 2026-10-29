"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_root as _support
from test_root import (
    Path,
    Refusal,
    TheDatabase,
    TheRoot,
    database_address,
    find_root,
    json,
    keychain_password,
    role,
    roots_folder,
    security_stand_in,
    tempfile,
    unittest,
    write,
)


class TheRoot(_support.TheRoot):
# TEST-TIER-BEGIN trunks/trivial/tests/test_root.py::TheRoot.test_the_root_json_names_the_database_and_the_version
    def test_the_root_json_names_the_database_and_the_version(self) -> None:
        write(roots_folder(self.home) / "rct" / "root.json", {"database": "arbol_rct", "rootContract": 1})
        root = find_root(self.home, "rct")
        self.assertEqual((root.database, root.root_contract), ("arbol_rct", 1))
        self.assertEqual(root.exchanges, self.home / "Library/Application Support/Arbol/roots/rct/exchanges")
# TEST-TIER-END trunks/trivial/tests/test_root.py::TheRoot.test_the_root_json_names_the_database_and_the_version

# TEST-TIER-BEGIN trunks/trivial/tests/test_root.py::TheRoot.test_a_root_without_a_readable_root_json_is_unknown
    def test_a_root_without_a_readable_root_json_is_unknown(self) -> None:
        for content in (None, "{", {"rootContract": 1}, [1]):
            with self.subTest(content=content):
                if content is not None:
                    write(roots_folder(self.home) / "rct" / "root.json", content)
                with self.assertRaises(Refusal) as caught:
                    find_root(self.home, "rct")
                self.assertEqual(caught.exception.code, "unknown_root")
# TEST-TIER-END trunks/trivial/tests/test_root.py::TheRoot.test_a_root_without_a_readable_root_json_is_unknown

# TEST-TIER-BEGIN trunks/trivial/tests/test_root.py::TheRoot.test_a_version_this_build_does_not_implement_is_a_contract_mismatch
    def test_a_version_this_build_does_not_implement_is_a_contract_mismatch(self) -> None:
        write(roots_folder(self.home) / "rct" / "root.json", {"database": "arbol_rct", "rootContract": 2})
        with self.assertRaises(Refusal) as caught:
            find_root(self.home, "rct")
        self.assertEqual(caught.exception.code, "contract_mismatch")
# TEST-TIER-END trunks/trivial/tests/test_root.py::TheRoot.test_a_version_this_build_does_not_implement_is_a_contract_mismatch



class TheDatabase(_support.TheDatabase):
# TEST-TIER-BEGIN trunks/trivial/tests/test_root.py::TheDatabase.test_the_address_comes_from_database_json_in_the_home_folder
    def test_the_address_comes_from_database_json_in_the_home_folder(self) -> None:
        write(self.home / ".arbol" / "database.json", {"address": "postgresql://rct@%2Ftmp%2Frct-1a2b"})
        address = database_address(self.home)
        self.assertEqual(address, "postgresql://rct@%2Ftmp%2Frct-1a2b")
        self.assertEqual(role(address), "rct")
        self.assertEqual(role("postgresql://arbol@127.0.0.1:5432"), "arbol")
# TEST-TIER-END trunks/trivial/tests/test_root.py::TheDatabase.test_the_address_comes_from_database_json_in_the_home_folder

# TEST-TIER-BEGIN trunks/trivial/tests/test_root.py::TheDatabase.test_without_an_address_the_database_is_unavailable
    def test_without_an_address_the_database_is_unavailable(self) -> None:
        for content in (None, {"host": "x"}, "nonsense"):
            with self.subTest(content=content):
                if content is not None:
                    write(self.home / ".arbol" / "database.json", content)
                with self.assertRaises(Refusal) as caught:
                    database_address(self.home)
                self.assertEqual(caught.exception.code, "database_unavailable")
# TEST-TIER-END trunks/trivial/tests/test_root.py::TheDatabase.test_without_an_address_the_database_is_unavailable

# TEST-TIER-BEGIN trunks/trivial/tests/test_root.py::TheDatabase.test_the_password_is_the_keychain_item_of_the_role
    def test_the_password_is_the_keychain_item_of_the_role(self) -> None:
        security = security_stand_in(self.home, password="pa ss")
        self.assertEqual(keychain_password("arbol", str(security)), "pa ss")
        self.assertEqual((self.home / "security.args").read_text(),
                         "find-generic-password -s com.sylvan-stack.arbol.database -a arbol -w\n")
# TEST-TIER-END trunks/trivial/tests/test_root.py::TheDatabase.test_the_password_is_the_keychain_item_of_the_role

# TEST-TIER-BEGIN trunks/trivial/tests/test_root.py::TheDatabase.test_exit_status_44_means_no_item_and_no_password
    def test_exit_status_44_means_no_item_and_no_password(self) -> None:
        self.assertIsNone(keychain_password("rct", str(security_stand_in(self.home, status=44))))
# TEST-TIER-END trunks/trivial/tests/test_root.py::TheDatabase.test_exit_status_44_means_no_item_and_no_password

# TEST-TIER-BEGIN trunks/trivial/tests/test_root.py::TheDatabase.test_another_failure_or_no_answer_within_2_seconds_is_refused_naming_the_keychain
    def test_another_failure_or_no_answer_within_2_seconds_is_refused_naming_the_keychain(self) -> None:
        for security in (security_stand_in(self.home, status=51), security_stand_in(self.home, sleep=3)):
            with self.subTest(security=security.read_text()), self.assertRaises(Refusal) as caught:
                keychain_password("rct", str(security))
            self.assertEqual(caught.exception.code, "database_unavailable")
            self.assertIn("Keychain", caught.exception.message)
# TEST-TIER-END trunks/trivial/tests/test_root.py::TheDatabase.test_another_failure_or_no_answer_within_2_seconds_is_refused_naming_the_keychain
