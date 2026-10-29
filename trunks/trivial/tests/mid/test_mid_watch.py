"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_watch as _support
from test_watch import (Path ,os ,signal ,subprocess ,sys ,tempfile ,time)


class WatchLifetime(_support.WatchLifetime):
# TEST-TIER-BEGIN trunks/trivial/tests/test_watch.py::WatchLifetime.test_run_starts_the_watch_before_acceptance_and_a_blocked_work_loop_cannot_stop_it
    def test_run_starts_the_watch_before_acceptance_and_a_blocked_work_loop_cannot_stop_it(self) -> None:
        source = Path(_support.__file__).resolve().parents[1] / "src"
        with tempfile.TemporaryDirectory() as name:
            marker = Path(name) / "work"
            script = f"""
import asyncio,sys,threading,time
from pathlib import Path
sys.path.insert(0,{str(source)!r})
import arbol_trunk_trivial.run as work
from arbol_trunk_trivial.termination import install_handlers
async def blocked(*args,**kwargs):
    Path({str(marker)!r}).write_text('working\\n')
    threading.Event().wait()
work.accept_message=blocked
install_handlers()
asyncio.run(work.run_exchange(None,None,build='0',process={{}},started=time.monotonic()))
"""
            began = time.monotonic()
            process = subprocess.Popen([sys.executable, "-I", "-B", "-c", script], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=True,
                                       env={**os.environ, "ARBOL_TEST_TIME_SCALE": "100"})
            try:
                output, error = process.communicate(timeout=5)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            self.assertIn(process.returncode, (-signal.SIGKILL, 128 + signal.SIGKILL), error.decode())
            self.assertEqual((output, error), (b"", b""))
            self.assertEqual(marker.read_text(), "working\n")
            self.assertGreaterEqual(time.monotonic() - began, 0.6)
# TEST-TIER-END trunks/trivial/tests/test_watch.py::WatchLifetime.test_run_starts_the_watch_before_acceptance_and_a_blocked_work_loop_cannot_stop_it
