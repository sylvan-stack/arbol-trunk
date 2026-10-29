
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_control.py::Control.test_it_reads_the_new_whole_lines_and_keeps_an_unfinished_one_until_it_is_whole
# Reason: Local JSON/text forwarding tables repeat the real retained slow-reader pipe and shared R9 question-control scenario. Case reviewed: It reads the new whole lines and keeps an unfinished one until it is whole.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_control.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_it_reads_the_new_whole_lines_and_keeps_an_unfinished_one_until_it_is_whole(self) -> None:
#         self.assertEqual(self.control.read(), [])
#         self.append(f"{STOP}\n{ANSWER}\n".encode() + b'{"type":"st')
#         self.assertEqual([(line.kind, line.text) for line in self.control.read()], [("stop", STOP), ("answer", ANSWER)])
#         self.assertEqual(self.control.read(), [])
#         self.append(b'op"}\n')
#         self.assertEqual([line.text for line in self.control.read()], [STOP])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_control.py::Control.test_each_line_keeps_its_own_text
# Reason: Local JSON/text forwarding tables repeat the real retained slow-reader pipe and shared R9 question-control scenario. Case reviewed: Each line keeps its own text.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_control.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_each_line_keeps_its_own_text(self) -> None:
#         text = '{ "askId" : "ask_1", "type" : "answer", "answer" : {"type": "decline"} }'
#         self.append(text.encode() + b"\n")
#         [line] = self.control.read()
#         self.assertEqual(line.text, text)
#         self.assertEqual(line.value["answer"], {"type": "decline"})
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_control.py::Control.test_a_line_it_does_not_know_is_ignored
# Reason: Local JSON/text forwarding tables repeat the real retained slow-reader pipe and shared R9 question-control scenario. Case reviewed: A line it does not know is ignored.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_control.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_line_it_does_not_know_is_ignored(self) -> None:
#         for raw in (b'{"type":"pause"}', b"not json", b"[1]", b'{"no":"type"}', b'{"type":"stop","x":NaN}',
#                     b'{"type":"stop","x":"\xff"}', b""):
#             self.append(raw + b"\n")
#         self.assertEqual(self.control.read(), [])
#         self.append(STOP.encode() + b"\n")
#         self.assertEqual(len(self.control.read()), 1)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_control.py::Control.test_the_file_is_never_written
# Reason: Local JSON/text forwarding tables repeat the real retained slow-reader pipe and shared R9 question-control scenario. Case reviewed: The file is never written.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_control.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_file_is_never_written(self) -> None:
#         self.append(STOP.encode() + b"\n")
#         os.chmod(self.path, 0o400)
#         control = ControlFile(self.path)
#         self.addCleanup(control.close)
#         self.assertEqual(len(control.read()), 1)
#         self.assertEqual(self.path.read_bytes(), STOP.encode() + b"\n")
# LOW-TIER-SOURCE-END
# LOW-TIER-END
