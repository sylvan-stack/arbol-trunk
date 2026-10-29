
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_storage.py::Storage.test_only_nul_and_lone_surrogates_change_and_a_whole_emoji_stays_whole
# Reason: Pure sanitization examples and generated-parameter inspection overlap retained real R17 PostgreSQL persistence across malformed Unicode. Case reviewed: Only nul and lone surrogates change and a whole emoji stays whole.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_storage.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_only_nul_and_lone_surrogates_change_and_a_whole_emoji_stays_whole(self) -> None:
#         value = {BAD: [BAD, "😀", "\ud83d\ude00", "é\n\t\\\"\ufeff", 0, False, None]}
#         self.assertEqual(stored(value), {GOOD: [GOOD, "😀", "😀", "é\n\t\\\"\ufeff", 0, False, None]})
#         self.assertEqual(value[BAD][:3], [BAD, "😀", "\ud83d\ude00"])
#         self.assertEqual([stored("\ud83d"), stored("\ude00")], ["\ufffd", "\ufffd"])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_storage.py::Storage.test_requests_and_records_keep_lone_surrogates_in_valid_utf8_json
# Reason: Pure sanitization examples and generated-parameter inspection overlap retained real R17 PostgreSQL persistence across malformed Unicode. Case reviewed: Requests and records keep lone surrogates in valid utf8 json.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_storage.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_requests_and_records_keep_lone_surrogates_in_valid_utf8_json(self) -> None:
#         value = {"message": BAD, "emoji": "😀"}
#         self.assertEqual(json.loads(encode(value).decode("utf-8")), value)
#         self.assertIn(b"\\ud83d", encode(value))
#         self.assertIn("😀".encode(), encode(value))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_storage.py::Storage.test_every_text_and_jsonb_parameter_is_safe_without_changing_the_rows
# Reason: Pure sanitization examples and generated-parameter inspection overlap retained real R17 PostgreSQL persistence across malformed Unicode. Case reviewed: Every text and jsonb parameter is safe without changing the rows.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_storage.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END
