import json
import os
import signal
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

from arbol_trunk_trivial.termination import end_group

SOURCE = Path(__file__).resolve().parents[1] / "src"


class Termination(unittest.TestCase):
    def test_term_then_kill_after_five_seconds_divided_by_the_time_scale(self) -> None:
        with (mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "10"}),
              mock.patch("arbol_trunk_trivial.termination.uptime", side_effect=[0.0, 0.0, 0.5]),
              mock.patch("arbol_trunk_trivial.termination.time.sleep") as sleep,
              mock.patch("arbol_trunk_trivial.termination.os.getpgrp", return_value=123),
              mock.patch("arbol_trunk_trivial.termination.os.killpg") as kill,
              mock.patch("arbol_trunk_trivial.termination.signal.signal") as ignore,
              mock.patch("arbol_trunk_trivial.termination.os._exit", side_effect=SystemExit),
              self.assertRaises(SystemExit)):
            end_group()
        self.assertEqual(kill.call_args_list, [mock.call(123, signal.SIGTERM), mock.call(123, signal.SIGKILL)])
        sleep.assert_called_once_with(0.5)
        self.assertEqual(ignore.call_args_list, [mock.call(n, signal.SIG_IGN)
                                               for n in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)])

    def test_the_group_is_killed_even_when_a_child_ignores_term(self) -> None:
        child = "import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);print('ready',flush=True);time.sleep(60)"
        script = f"""
import json,os,subprocess,sys
sys.path.insert(0,{str(SOURCE)!r})
from arbol_trunk_trivial.termination import end_group
p=subprocess.Popen([sys.executable,'-c',{child!r}],stdout=subprocess.PIPE,text=True)
assert p.stdout.readline() == 'ready\\n'
print(json.dumps({{'child':p.pid}}),flush=True)
end_group()
"""
        began = time.monotonic()
        process = subprocess.Popen([sys.executable, "-I", "-c", script], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True,
                                   env={**os.environ, "ARBOL_TEST_TIME_SCALE": "10"})
        try:
            out, err = process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        self.assertEqual(process.returncode, -signal.SIGKILL, err.decode())
        self.assertGreaterEqual(time.monotonic() - began, 0.5)
        child_pid = json.loads(out)["child"]
        state = subprocess.run(["/bin/ps", "-o", "stat=", "-p", str(child_pid)], capture_output=True,
                               text=True, check=False).stdout.strip()
        self.assertTrue(not state or state.startswith("Z"), state)
