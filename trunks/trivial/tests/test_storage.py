import unittest
from datetime import UTC, datetime
from typing import Any

from psycopg.types.json import Jsonb

from arbol_trunk_trivial.rows import MessageRow, Row, RunRow, ToolCallRow
from arbol_trunk_trivial.storage import stored

BAD = "A\0\ud83dB\ude00"
GOOD = "A\ufffd\ufffdB\ufffd"


class Storage(unittest.TestCase):
    def test_only_nul_and_lone_surrogates_change_and_a_whole_emoji_stays_whole(self) -> None:
        value = {BAD: [BAD, "😀", "\ud83d\ude00", "é\n\t\\\"\ufeff", 0, False, None]}
        self.assertEqual(stored(value), {GOOD: [GOOD, "😀", "😀", "é\n\t\\\"\ufeff", 0, False, None]})
        self.assertEqual(value[BAD][:3], [BAD, "😀", "\ud83d\ude00"])
        self.assertEqual([stored("\ud83d"), stored("\ude00")], ["\ufffd", "\ufffd"])

    def test_every_text_and_jsonb_parameter_is_safe_without_changing_the_rows(self) -> None:
        rows: list[Row] = [MessageRow("x", 2, BAD),
                ToolCallRow("x", 3, BAD, BAD, BAD, BAD, {BAD: [BAD]}, True, [BAD], BAD,
                            ask={"question": BAD}, answer={"answer": BAD}),
                RunRow("x", BAD, "agent", "failed", {"model": BAD}, {"message": BAD}, {"model": BAD}, datetime.now(UTC))]

        def strings(value: Any) -> list[str]:
            if isinstance(value, str):
                return [value]
            if isinstance(value, Jsonb):
                return strings(value.obj)
            if isinstance(value, dict):
                return [text for pair in value.items() for item in pair for text in strings(item)]
            if isinstance(value, (list, tuple)):
                return [text for item in value for text in strings(item)]
            return []

        for row in rows:
            values = strings(row.statement()[1])
            self.assertIn(GOOD, values)
            self.assertNotIn(BAD, values)
        self.assertEqual(rows[0].text, BAD)  # type: ignore[union-attr]
