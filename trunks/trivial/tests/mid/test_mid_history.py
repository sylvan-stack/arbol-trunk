
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_history.py::History.test_the_example_of_trv_0
# Reason: Straightforward sorting/filtering/field-copy examples repeat history observations in retained real R5 and R14 contract scenarios. Case reviewed: The example of trv 0.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_history.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_example_of_trv_0(self) -> None:
#         rows = [
#             message(1, 0, "What does build.sh do?"),
#             message(1, 3, "Let me read it."),
#             HistoryRow(1, 4, name="shell", input={"command": "cat build.sh"}, ok=True,
#                        result={"output": "#!/bin/sh\nset -e\n…", "exitCode": 0}),
#             message(1, 6, "It compiles the three packages and copies them to dist/."),
#         ]
#         self.assertEqual(make_history(reversed(rows), before=2), [
#             {"type": "message", "role": "user", "text": "What does build.sh do?"},
#             {"type": "message", "role": "assistant", "text": "Let me read it."},
#             {"type": "tool_call", "name": "shell", "input": {"command": "cat build.sh"}, "ok": True,
#              "result": {"output": "#!/bin/sh\nset -e\n…", "exitCode": 0}},
#             {"type": "message", "role": "assistant", "text": "It compiles the three packages and copies them to dist/."},
#         ])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_history.py::History.test_exchanges_in_the_order_of_their_numbers_whatever_their_end_and_replaced_ones_left_out
# Reason: Straightforward sorting/filtering/field-copy examples repeat history observations in retained real R5 and R14 contract scenarios. Case reviewed: Exchanges in the order of their numbers whatever their end and replaced ones left out.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_history.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_exchanges_in_the_order_of_their_numbers_whatever_their_end_and_replaced_ones_left_out(self) -> None:
#         rows = [
#             message(3, 0, "third"), message(1, 0, "first"), message(1, 2, "answer one"),
#             message(2, 0, "second, replaced", replaced=True), message(2, 5, "its answer", replaced=True),
#             message(3, 4, "half an answer before it failed"),
#             message(4, 0, "the message being accepted"),
#         ]
#         self.assertEqual([item["text"] for item in make_history(rows, before=4)],
#                          ["first", "answer one", "third", "half an answer before it failed"])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_history.py::History.test_sub_agent_calls_are_left_out_and_null_result_and_error_too
# Reason: Straightforward sorting/filtering/field-copy examples repeat history observations in retained real R5 and R14 contract scenarios. Case reviewed: Sub agent calls are left out and null result and error too.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_history.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_sub_agent_calls_are_left_out_and_null_result_and_error_too(self) -> None:
#         rows = [
#             message(1, 0, "go"),
#             HistoryRow(1, 2, name="Task", input={"prompt": "look"}, ok=True, result="done"),
#             HistoryRow(1, 3, name="Read", input={"file_path": "/a"}, ok=True, result="x", parent_call_id="call_2"),
#             HistoryRow(1, 5, name="shell", input={"command": "false"}, ok=False, error="exit code 1"),
#             HistoryRow(1, 6, name="shell", input={"command": "sleep 9"}, ok=False),
#         ]
#         self.assertEqual(make_history(rows, before=2)[1:], [
#             {"type": "tool_call", "name": "Task", "input": {"prompt": "look"}, "ok": True, "result": "done"},
#             {"type": "tool_call", "name": "shell", "input": {"command": "false"}, "ok": False, "error": "exit code 1"},
#             {"type": "tool_call", "name": "shell", "input": {"command": "sleep 9"}, "ok": False},
#         ])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_history.py::History.test_the_text_of_an_answer_goes_back_exactly_as_it_was_saved
# Reason: Straightforward sorting/filtering/field-copy examples repeat history observations in retained real R5 and R14 contract scenarios. Case reviewed: The text of an answer goes back exactly as it was saved.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_history.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_text_of_an_answer_goes_back_exactly_as_it_was_saved(self) -> None:
#         text = "  two spaces, a tab\t, a replaced character � and a newline at the end\n"
#         self.assertEqual(make_history([message(1, 0, "q"), message(1, 1, text)], before=2)[1]["text"], text)
# LOW-TIER-SOURCE-END
# LOW-TIER-END
