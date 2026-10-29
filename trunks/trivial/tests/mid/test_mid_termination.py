"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_termination as _support
from test_termination import (Path ,SOURCE ,os ,signal ,subprocess ,sys ,tempfile)


class Termination(_support.Termination):


# TEST-TIER-BEGIN trunks/trivial/tests/test_termination.py::Termination.test_main_handles_term_int_and_foreground_hup_without_unwinding_to_an_end
    def test_main_handles_term_int_and_foreground_hup_without_unwinding_to_an_end(self) -> None:
        for number in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            with self.subTest(signal=number), tempfile.TemporaryDirectory() as name:
                path = Path(name) / "events.jsonl"
                script = f"""
import asyncio,sys
from pathlib import Path
sys.path.insert(0,{str(SOURCE)!r})
from arbol_trunk_trivial import cli
async def work(*args,**kwargs):
    path=Path({str(path)!r})
    path.write_text('accepted\\n')
    print('ready',flush=True)
    try:
        await asyncio.sleep(60)
    finally:
        with path.open('a') as stream: stream.write('end\\n')
cli.start=work
cli.main(['--root','rct','run','hello'])
"""
                process = subprocess.Popen([sys.executable, "-I", "-c", script], stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, start_new_session=True,
                                           env={**os.environ, "ARBOL_TEST_TIME_SCALE": "10"})
                try:
                    assert process.stdout is not None
                    self.assertEqual(process.stdout.readline(), b"ready\n")
                    process.send_signal(number)
                    _out, err = process.communicate(timeout=10)
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                self.assertIn(process.returncode, (-signal.SIGKILL, 128 + signal.SIGKILL), err.decode())
                self.assertEqual(path.read_text(), "accepted\n")
# TEST-TIER-END trunks/trivial/tests/test_termination.py::Termination.test_main_handles_term_int_and_foreground_hup_without_unwinding_to_an_end
