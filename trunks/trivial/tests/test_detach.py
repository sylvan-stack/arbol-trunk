import json
import os
import select
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "src"
CHILD = """
import json, os, signal, sys, time
sys.path.insert(0, {source!r})
from arbol_trunk_trivial.detach import detach, lead_process_group
lead_process_group()
print('{{"accepted":true}}', flush=True)
detach()
print("after the line", flush=True)
os.kill(os.getpid(), signal.SIGHUP)
time.sleep(0.3)
null = os.stat(os.devnull)
report = {{"pid": os.getpid(), "pgid": os.getpgrp(),
          "null": [os.path.samestat(os.fstat(descriptor), null) for descriptor in (0, 1, 2)]}}
with open({report!r}, "w") as f:
    json.dump(report, f)
"""


class Background(unittest.TestCase):
    def run_child(self, *, new_session: bool) -> tuple[str, dict[str, object], subprocess.Popen[bytes]]:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        report = Path(folder.name) / "report.json"
        child = subprocess.Popen([sys.executable, "-I", "-c", CHILD.format(source=str(SOURCE), report=str(report))],
                                 stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, start_new_session=new_session)
        assert child.stdout is not None
        ready, _, _ = select.select([child.stdout], [], [], 10)
        self.assertTrue(ready)
        line = child.stdout.readline().decode()
        child.stdout.close()  # the starter closes its end of the pipe, as arbol-root does
        deadline = time.monotonic() + 10
        while not report.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        child.wait(10)
        return line, json.loads(report.read_text()), child

    def test_after_the_line_its_output_goes_nowhere_and_sighup_is_ignored(self) -> None:
        line, report, child = self.run_child(new_session=True)
        self.assertEqual(line, '{"accepted":true}\n')
        self.assertEqual(child.returncode, 0)  # it lived on through SIGHUP and the closed pipe
        self.assertEqual(report["pgid"], report["pid"])
        self.assertEqual(report["null"], [True, True, True])

    def test_a_trunk_that_does_not_lead_its_group_makes_itself_the_leader_of_a_new_one(self) -> None:
        _line, report, child = self.run_child(new_session=False)
        self.assertEqual(child.returncode, 0)
        self.assertEqual(report["pgid"], report["pid"])
        self.assertNotEqual(report["pgid"], os.getpgrp())


if __name__ == "__main__":
    unittest.main()
