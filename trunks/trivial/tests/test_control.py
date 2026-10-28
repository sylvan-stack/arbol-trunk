"""Reading `control` (RCT-1.7)."""

import os
import tempfile
import unittest
from pathlib import Path

from arbol_trunk_trivial.control import ControlFile

STOP = '{"type":"stop"}'
ANSWER = '{"type":"answer","askId":"ask_1","answer":{"type":"answers","answers":{"branch":["main"]}}}'


class Control(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "control"
        self.path.write_bytes(b"")
        self.control = ControlFile(self.path)
        self.addCleanup(self.control.close)

    def append(self, data: bytes) -> None:
        descriptor = os.open(self.path, os.O_WRONLY | os.O_APPEND)
        try:
            os.write(descriptor, data)
        finally:
            os.close(descriptor)

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_control.py::Control.test_it_reads_the_new_whole_lines_and_keeps_an_unfinished_one_until_it_is_whole
#     def test_it_reads_the_new_whole_lines_and_keeps_an_unfinished_one_until_it_is_whole(self) -> None:
#         self.assertEqual(self.control.read(), [])
#         self.append(f"{STOP}\n{ANSWER}\n".encode() + b'{"type":"st')
#         self.assertEqual([(line.kind, line.text) for line in self.control.read()], [("stop", STOP), ("answer", ANSWER)])
#         self.assertEqual(self.control.read(), [])
#         self.append(b'op"}\n')
#         self.assertEqual([line.text for line in self.control.read()], [STOP])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_control.py::Control.test_it_reads_the_new_whole_lines_and_keeps_an_unfinished_one_until_it_is_whole

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_control.py::Control.test_each_line_keeps_its_own_text
#     def test_each_line_keeps_its_own_text(self) -> None:
#         text = '{ "askId" : "ask_1", "type" : "answer", "answer" : {"type": "decline"} }'
#         self.append(text.encode() + b"\n")
#         [line] = self.control.read()
#         self.assertEqual(line.text, text)
#         self.assertEqual(line.value["answer"], {"type": "decline"})
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_control.py::Control.test_each_line_keeps_its_own_text

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_control.py::Control.test_a_line_it_does_not_know_is_ignored
#     def test_a_line_it_does_not_know_is_ignored(self) -> None:
#         for raw in (b'{"type":"pause"}', b"not json", b"[1]", b'{"no":"type"}', b'{"type":"stop","x":NaN}',
#                     b'{"type":"stop","x":"\xff"}', b""):
#             self.append(raw + b"\n")
#         self.assertEqual(self.control.read(), [])
#         self.append(STOP.encode() + b"\n")
#         self.assertEqual(len(self.control.read()), 1)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_control.py::Control.test_a_line_it_does_not_know_is_ignored

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_control.py::Control.test_the_file_is_never_written
#     def test_the_file_is_never_written(self) -> None:
#         self.append(STOP.encode() + b"\n")
#         os.chmod(self.path, 0o400)
#         control = ControlFile(self.path)
#         self.addCleanup(control.close)
#         self.assertEqual(len(control.read()), 1)
#         self.assertEqual(self.path.read_bytes(), STOP.encode() + b"\n")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_control.py::Control.test_the_file_is_never_written


if __name__ == "__main__":
    unittest.main()
