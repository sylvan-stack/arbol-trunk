import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from fake_driver import MovedClock

from arbol_trunk_trivial.life import SignsOfLife
from arbol_trunk_trivial.watch import Watch


class Watching(unittest.TestCase):
    def test_only_sixty_awake_seconds_without_a_raise_trigger_the_end(self) -> None:
        clock = MovedClock()
        life = SignsOfLife(clock=clock)
        ended: list[float] = []
        watch = Watch(life, lambda: ended.append(clock.now()))
        clock.t += 59
        self.assertFalse(watch.look())
        self.assertEqual(ended, [])
        life.beat()
        clock.t += 59
        self.assertFalse(watch.look())
        clock.t += 1
        self.assertTrue(watch.look())
        self.assertEqual(ended, [clock.t])
        self.assertEqual(life.heartbeat, 1)

    def test_a_wall_clock_jump_does_not_count_as_awake_time(self) -> None:
        clock = MovedClock()
        life = SignsOfLife(clock=clock)
        ended = mock.Mock()
        watch = Watch(life, ended)
        with mock.patch('time.time', return_value=10**12):
            self.assertFalse(watch.look())
        ended.assert_not_called()

    def test_the_second_thread_observes_the_clock_but_never_raises_the_heartbeat(self) -> None:
        clock = MovedClock()
        life = SignsOfLife(clock=clock)
        ended = threading.Event()
        watch = Watch(life, ended.set)
        clock.t += 60
        with mock.patch('arbol_trunk_trivial.watch.LOOK_SECONDS', 0.001):
            watch.start()
            try:
                self.assertTrue(ended.wait(1))
                self.assertEqual(life.heartbeat, 0)
                self.assertEqual(life.last_raised, clock.start)
            finally:
                watch.close()
        self.assertIsNone(watch.thread)

    def test_closing_a_watch_does_not_wait_for_another_look(self) -> None:
        life = SignsOfLife(clock=MovedClock())
        ended = mock.Mock()
        watch = Watch(life, ended)
        watch.start()
        watch.close()
        ended.assert_not_called()
        self.assertIsNone(watch.thread)


class EndingTheGroup(unittest.TestCase):
    def test_the_watch_uses_shared_group_termination_without_raising_or_writing(self) -> None:
        clock = MovedClock()
        life = SignsOfLife(clock=clock)
        clock.t += 60
        with mock.patch('arbol_trunk_trivial.watch.end_group') as end:
            watch = Watch(life)
            self.assertTrue(watch.look())
        end.assert_called_once_with()
        self.assertEqual(life.heartbeat, 0)
        self.assertEqual(life.last_raised, clock.start)


class WatchLifetime(unittest.TestCase):
    def test_run_starts_the_watch_before_acceptance_and_a_blocked_work_loop_cannot_stop_it(self) -> None:
        source = Path(__file__).resolve().parents[1] / "src"
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
