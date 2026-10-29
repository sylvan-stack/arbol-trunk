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

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_watch.py::Watching.test_only_sixty_awake_seconds_without_a_raise_trigger_the_end
# Reason: Local clock/callback tables and the post-first-event hang duplicate the real R7 contract scenario; retain the earlier blocked-acceptance process boundary. Case reviewed: Only sixty awake seconds without a raise trigger the end.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_watch.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_only_sixty_awake_seconds_without_a_raise_trigger_the_end(self) -> None:
#         clock = MovedClock()
#         life = SignsOfLife(clock=clock)
#         ended: list[float] = []
#         watch = Watch(life, lambda: ended.append(clock.now()))
#         clock.t += 59
#         self.assertFalse(watch.look())
#         self.assertEqual(ended, [])
#         life.beat()
#         clock.t += 59
#         self.assertFalse(watch.look())
#         clock.t += 1
#         self.assertTrue(watch.look())
#         self.assertEqual(ended, [clock.t])
#         self.assertEqual(life.heartbeat, 1)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_watch.py::Watching.test_a_wall_clock_jump_does_not_count_as_awake_time
# Reason: Local clock/callback tables and the post-first-event hang duplicate the real R7 contract scenario; retain the earlier blocked-acceptance process boundary. Case reviewed: A wall clock jump does not count as awake time.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_watch.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_wall_clock_jump_does_not_count_as_awake_time(self) -> None:
#         clock = MovedClock()
#         life = SignsOfLife(clock=clock)
#         ended = mock.Mock()
#         watch = Watch(life, ended)
#         with mock.patch('time.time', return_value=10**12):
#             self.assertFalse(watch.look())
#         ended.assert_not_called()
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_watch.py::Watching.test_the_second_thread_observes_the_clock_but_never_raises_the_heartbeat
# Reason: Local clock/callback tables and the post-first-event hang duplicate the real R7 contract scenario; retain the earlier blocked-acceptance process boundary. Case reviewed: The second thread observes the clock but never raises the heartbeat.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_watch.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_second_thread_observes_the_clock_but_never_raises_the_heartbeat(self) -> None:
#         clock = MovedClock()
#         life = SignsOfLife(clock=clock)
#         ended = threading.Event()
#         watch = Watch(life, ended.set)
#         clock.t += 60
#         with mock.patch('arbol_trunk_trivial.watch.LOOK_SECONDS', 0.001):
#             watch.start()
#             try:
#                 self.assertTrue(ended.wait(1))
#                 self.assertEqual(life.heartbeat, 0)
#                 self.assertEqual(life.last_raised, clock.start)
#             finally:
#                 watch.close()
#         self.assertIsNone(watch.thread)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_watch.py::Watching.test_closing_a_watch_does_not_wait_for_another_look
# Reason: Local clock/callback tables and the post-first-event hang duplicate the real R7 contract scenario; retain the earlier blocked-acceptance process boundary. Case reviewed: Closing a watch does not wait for another look.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_watch.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_closing_a_watch_does_not_wait_for_another_look(self) -> None:
#         life = SignsOfLife(clock=MovedClock())
#         ended = mock.Mock()
#         watch = Watch(life, ended)
#         watch.start()
#         watch.close()
#         ended.assert_not_called()
#         self.assertIsNone(watch.thread)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_watch.py::EndingTheGroup.test_the_watch_uses_shared_group_termination_without_raising_or_writing
# Reason: Local clock/callback tables and the post-first-event hang duplicate the real R7 contract scenario; retain the earlier blocked-acceptance process boundary. Case reviewed: The watch uses shared group termination without raising or writing.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_watch.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_watch_uses_shared_group_termination_without_raising_or_writing(self) -> None:
#         clock = MovedClock()
#         life = SignsOfLife(clock=clock)
#         clock.t += 60
#         with mock.patch('arbol_trunk_trivial.watch.end_group') as end:
#             watch = Watch(life)
#             self.assertTrue(watch.look())
#         end.assert_called_once_with()
#         self.assertEqual(life.heartbeat, 0)
#         self.assertEqual(life.last_raised, clock.start)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_watch.py::DeliberateHang.test_the_first_event_is_whole_and_no_later_event_or_end_is_written
# Reason: Local clock/callback tables and the post-first-event hang duplicate the real R7 contract scenario; retain the earlier blocked-acceptance process boundary. Case reviewed: The first event is whole and no later event or end is written.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_watch.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_first_event_is_whole_and_no_later_event_or_end_is_written(self) -> None:
#         source = Path(_support.__file__).resolve().parents[1] / "src"
#         tests = Path(_support.__file__).resolve().parent
#         with tempfile.TemporaryDirectory() as name:
#             folder = Path(name)
#             script = f"""
# import asyncio,sys
# from pathlib import Path
# sys.path[:0]=[{str(source)!r},{str(tests)!r}]
# from fake_driver import MovedClock,ScriptedDriver,event
# from fakes import FakeDatabase
# from arbol_trunk_trivial.events import EventsFile
# from arbol_trunk_trivial.folder import ExchangeFolder
# from arbol_trunk_trivial.life import SignsOfLife
# from arbol_trunk_trivial.rows import RowMaker
# from arbol_trunk_trivial.run import drive
# from arbol_trunk_trivial.saver import Saver
# from arbol_trunk_trivial.termination import install_handlers
# from arbol_trunk_trivial.watch import Watch
# install_handlers()
# record={{'signsOfLife':{{'heartbeat':0,'waitingFor':'driver','since':'2026-10-26T11:00:00.000Z'}}}}
# folder=ExchangeFolder.make(Path({name!r}), 'exchange', record)
# life=SignsOfLife(folder)
# watch=Watch(life);watch.start()
# clock=MovedClock();driver=ScriptedDriver(clock)
# driver.at(0,'event',event(1,'started'))
# driver.at(0.1,'event',event(2,'text',text='must not arrive'))
# asyncio.run(drive(driver,EventsFile(folder.path/'events.jsonl'),RowMaker('exchange'),
#                   Saver(FakeDatabase().connect()),clock=clock,life=life))
# """
#             process = subprocess.Popen([sys.executable, "-I", "-B", "-c", script], stdout=subprocess.PIPE,
#                                        stderr=subprocess.PIPE, start_new_session=True,
#                                        env={**os.environ, "ARBOL_TEST_TIME_SCALE": "100", "ARBOL_TEST_HANG": "1"})
#             try:
#                 output, error = process.communicate(timeout=5)
#             finally:
#                 if process.poll() is None:
#                     os.killpg(process.pid, signal.SIGKILL)
#                     process.wait()
#             self.assertIn(process.returncode, (-signal.SIGKILL, 128 + signal.SIGKILL), error.decode())
#             self.assertEqual((output, error), (b"", b""))
#             import json
#             data = (folder / 'exchange/events.jsonl').read_bytes()
#             self.assertTrue(data.endswith(b'\n'))
#             lines = [json.loads(line) for line in data.splitlines()]
#             self.assertEqual(len(lines), 1)
#             self.assertEqual((lines[0]['n'], lines[0]['event']['type']), (1, 'started'))
#             record = json.loads((folder / 'exchange/record.json').read_text())
#             self.assertNotIn('end', record)
# LOW-TIER-SOURCE-END
# LOW-TIER-END
