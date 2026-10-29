"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_storage as _support
# from test_storage import (
#     BAD,
#     GOOD,
#     Storage,
#     unittest,
# )


# class Storage(_support.Storage):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_storage.py::Storage.test_only_nul_and_lone_surrogates_change_and_a_whole_emoji_stays_whole
#     def test_only_nul_and_lone_surrogates_change_and_a_whole_emoji_stays_whole(self) -> None:
#         value = {BAD: [BAD, "😀", "\ud83d\ude00", "é\n\t\\\"\ufeff", 0, False, None]}
#         self.assertEqual(stored(value), {GOOD: [GOOD, "😀", "😀", "é\n\t\\\"\ufeff", 0, False, None]})
#         self.assertEqual(value[BAD][:3], [BAD, "😀", "\ud83d\ude00"])
#         self.assertEqual([stored("\ud83d"), stored("\ude00")], ["\ufffd", "\ufffd"])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_storage.py::Storage.test_only_nul_and_lone_surrogates_change_and_a_whole_emoji_stays_whole

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_storage.py::Storage.test_requests_and_records_keep_lone_surrogates_in_valid_utf8_json
#     def test_requests_and_records_keep_lone_surrogates_in_valid_utf8_json(self) -> None:
#         value = {"message": BAD, "emoji": "😀"}
#         self.assertEqual(json.loads(encode(value).decode("utf-8")), value)
#         self.assertIn(b"\\ud83d", encode(value))
#         self.assertIn("😀".encode(), encode(value))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_storage.py::Storage.test_requests_and_records_keep_lone_surrogates_in_valid_utf8_json

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_storage.py::Storage.test_every_text_and_jsonb_parameter_is_safe_without_changing_the_rows
#     def test_every_text_and_jsonb_parameter_is_safe_without_changing_the_rows(self) -> None:
#         rows: list[Row] = [MessageRow("x", 2, BAD),
#                 ToolCallRow("x", 3, BAD, BAD, BAD, BAD, {BAD: [BAD]}, True, [BAD], BAD,
#                             ask={"question": BAD}, answer={"answer": BAD}),
#                 RunRow("x", BAD, "agent", "failed", {"model": BAD}, {"message": BAD}, {"model": BAD}, datetime.now(UTC))]
#
#         def strings(value: Any) -> list[str]:
#             if isinstance(value, str):
#                 return [value]
#             if isinstance(value, Jsonb):
#                 return strings(value.obj)
#             if isinstance(value, dict):
#                 return [text for pair in value.items() for item in pair for text in strings(item)]
#             if isinstance(value, (list, tuple)):
#                 return [text for item in value for text in strings(item)]
#             return []
#
#         for row in rows:
#             values = strings(row.statement()[1])
#             self.assertIn(GOOD, values)
#             self.assertNotIn(BAD, values)
#         self.assertEqual(rows[0].text, BAD)  # type: ignore[union-attr]
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_storage.py::Storage.test_every_text_and_jsonb_parameter_is_safe_without_changing_the_rows


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_storage.py:1
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_storage.py:1

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_storage.py:3
# from datetime import UTC, datetime
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_storage.py:3

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_storage.py:4
# from typing import Any
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_storage.py:4

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_storage.py:6
# from psycopg.types.json import Jsonb
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_storage.py:6

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_storage.py:8
# from arbol_trunk_trivial.folder import encode
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_storage.py:8

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_storage.py:9
# from arbol_trunk_trivial.rows import MessageRow, Row, RunRow, ToolCallRow
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_storage.py:9

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_storage.py:10
# from arbol_trunk_trivial.storage import stored
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_storage.py:10

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
