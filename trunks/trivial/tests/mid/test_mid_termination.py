"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_termination as _support
# from test_termination import (
#     Path,
#     SOURCE,
#     Termination,
#     unittest,
# )


# class Termination(_support.Termination):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_termination.py::Termination.test_term_then_kill_after_five_seconds_divided_by_the_time_scale
#     def test_term_then_kill_after_five_seconds_divided_by_the_time_scale(self) -> None:
#         with (mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "10"}),
#               mock.patch("arbol_trunk_trivial.termination.uptime", side_effect=[0.0, 0.0, 0.5]),
#               mock.patch("arbol_trunk_trivial.termination.time.sleep") as sleep,
#               mock.patch("arbol_trunk_trivial.termination.os.getpgrp", return_value=123),
#               mock.patch("arbol_trunk_trivial.termination.os.killpg") as kill,
#               mock.patch("arbol_trunk_trivial.termination.signal.signal") as ignore,
#               mock.patch("arbol_trunk_trivial.termination.os._exit", side_effect=SystemExit),
#               self.assertRaises(SystemExit)):
#             end_group()
#         self.assertEqual(kill.call_args_list, [mock.call(123, signal.SIGTERM), mock.call(123, signal.SIGKILL)])
#         sleep.assert_called_once_with(0.5)
#         self.assertEqual(ignore.call_args_list, [mock.call(n, signal.SIG_IGN)
#                                                for n in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_termination.py::Termination.test_term_then_kill_after_five_seconds_divided_by_the_time_scale

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_termination.py::Termination.test_the_group_is_killed_even_when_a_child_ignores_term
#     def test_the_group_is_killed_even_when_a_child_ignores_term(self) -> None:
#         child = "import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);print('ready',flush=True);time.sleep(60)"
#         script = f"""
# import json,os,subprocess,sys
# sys.path.insert(0,{str(SOURCE)!r})
# from arbol_trunk_trivial.termination import end_group
# p=subprocess.Popen([sys.executable,'-c',{child!r}],stdout=subprocess.PIPE,text=True)
# assert p.stdout.readline() == 'ready\\n'
# print(json.dumps({{'child':p.pid}}),flush=True)
# end_group()
# """
#         began = time.monotonic()
#         process = subprocess.Popen([sys.executable, "-I", "-c", script], stdout=subprocess.PIPE,
#                                    stderr=subprocess.PIPE, start_new_session=True,
#                                    env={**os.environ, "ARBOL_TEST_TIME_SCALE": "10"})
#         try:
#             out, err = process.communicate(timeout=10)
#         finally:
#             if process.poll() is None:
#                 os.killpg(process.pid, signal.SIGKILL)
#                 process.wait()
#         self.assertIn(process.returncode, (-signal.SIGKILL, 128 + signal.SIGKILL), err.decode())
#         self.assertGreaterEqual(time.monotonic() - began, 0.5)
#         child_pid = json.loads(out)["child"]
#         state = subprocess.run(["/bin/ps", "-o", "stat=", "-p", str(child_pid)], capture_output=True,
#                                text=True, check=False).stdout.strip()
#         self.assertTrue(not state or state.startswith("Z"), state)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_termination.py::Termination.test_the_group_is_killed_even_when_a_child_ignores_term

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_termination.py::Termination.test_main_handles_term_int_and_foreground_hup_without_unwinding_to_an_end
#     def test_main_handles_term_int_and_foreground_hup_without_unwinding_to_an_end(self) -> None:
#         for number in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
#             with self.subTest(signal=number), tempfile.TemporaryDirectory() as name:
#                 path = Path(name) / "events.jsonl"
#                 script = f"""
# import asyncio,sys
# from pathlib import Path
# sys.path.insert(0,{str(SOURCE)!r})
# from arbol_trunk_trivial import cli
# async def work(*args,**kwargs):
#     path=Path({str(path)!r})
#     path.write_text('accepted\\n')
#     print('ready',flush=True)
#     try:
#         await asyncio.sleep(60)
#     finally:
#         with path.open('a') as stream: stream.write('end\\n')
# cli.start=work
# cli.main(['--root','rct','run','hello'])
# """
#                 process = subprocess.Popen([sys.executable, "-I", "-c", script], stdout=subprocess.PIPE,
#                                            stderr=subprocess.PIPE, start_new_session=True,
#                                            env={**os.environ, "ARBOL_TEST_TIME_SCALE": "10"})
#                 try:
#                     assert process.stdout is not None
#                     self.assertEqual(process.stdout.readline(), b"ready\n")
#                     process.send_signal(number)
#                     _out, err = process.communicate(timeout=10)
#                 finally:
#                     if process.poll() is None:
#                         os.killpg(process.pid, signal.SIGKILL)
#                         process.wait()
#                 self.assertIn(process.returncode, (-signal.SIGKILL, 128 + signal.SIGKILL), err.decode())
#                 self.assertEqual(path.read_text(), "accepted\n")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_termination.py::Termination.test_main_handles_term_int_and_foreground_hup_without_unwinding_to_an_end

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_termination.py::Termination.test_term_reaches_the_driver_which_ends_its_vendor_group
#     def test_term_reaches_the_driver_which_ends_its_vendor_group(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             report = Path(name) / "vendor.json"
#             vendor = "import time;print('ready',flush=True);time.sleep(60)"
#             driver = f"""
# import json,os,signal,subprocess,sys,time
# from pathlib import Path
# p=subprocess.Popen([sys.executable,'-c',{vendor!r}],stdout=subprocess.PIPE,start_new_session=True)
# assert p.stdout.readline() == b'ready\\n'
# def stop(*args):
#     os.killpg(p.pid,signal.SIGTERM)
#     p.wait(2)
#     Path({str(report)!r}).write_text(json.dumps({{'pid':p.pid,'ended':True}}))
#     sys.exit(0)
# signal.signal(signal.SIGTERM,stop)
# print('ready',flush=True)
# time.sleep(60)
# """
#             trunk = f"""
# import subprocess,sys
# sys.path.insert(0,{str(SOURCE)!r})
# from arbol_trunk_trivial.termination import end_group
# p=subprocess.Popen([sys.executable,'-c',{driver!r}],stdout=subprocess.PIPE)
# assert p.stdout.readline() == b'ready\\n'
# end_group()
# """
#             process = subprocess.Popen([sys.executable, "-I", "-c", trunk], stdout=subprocess.PIPE,
#                                        stderr=subprocess.PIPE, start_new_session=True,
#                                        env={**os.environ, "ARBOL_TEST_TIME_SCALE": "10"})
#             try:
#                 _out, err = process.communicate(timeout=10)
#             finally:
#                 if process.poll() is None:
#                     os.killpg(process.pid, signal.SIGKILL)
#                     process.wait()
#             self.assertIn(process.returncode, (-signal.SIGKILL, 128 + signal.SIGKILL), err.decode())
#             self.assertTrue(json.loads(report.read_text())["ended"])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_termination.py::Termination.test_term_reaches_the_driver_which_ends_its_vendor_group

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_termination.py::Termination.test_a_watch_thread_can_end_the_group_without_main_thread_signal_api_calls
#     def test_a_watch_thread_can_end_the_group_without_main_thread_signal_api_calls(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             path = Path(name) / "events.jsonl"
#             script = f"""
# import sys,threading,time
# from pathlib import Path
# sys.path.insert(0,{str(SOURCE)!r})
# from arbol_trunk_trivial.termination import end_group,install_handlers
# install_handlers()
# Path({str(path)!r}).write_text('accepted\\n')
# threading.Thread(target=end_group).start()
# try:
#     time.sleep(60)
# finally:
#     with Path({str(path)!r}).open('a') as stream: stream.write('end\\n')
# """
#             process = subprocess.Popen([sys.executable, "-I", "-c", script], stdout=subprocess.PIPE,
#                                        stderr=subprocess.PIPE, start_new_session=True,
#                                        env={**os.environ, "ARBOL_TEST_TIME_SCALE": "10"})
#             try:
#                 _out, err = process.communicate(timeout=10)
#             finally:
#                 if process.poll() is None:
#                     os.killpg(process.pid, signal.SIGKILL)
#                     process.wait()
#             self.assertIn(process.returncode, (-signal.SIGKILL, 128 + signal.SIGKILL), err.decode())
#             self.assertEqual(err, b"")
#             self.assertEqual(path.read_text(), "accepted\n")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_termination.py::Termination.test_a_watch_thread_can_end_the_group_without_main_thread_signal_api_calls


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_termination.py:1
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_termination.py:1

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_termination.py:2
# import os
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_termination.py:2

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_termination.py:3
# import signal
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_termination.py:3

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_termination.py:4
# import subprocess
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_termination.py:4

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_termination.py:5
# import sys
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_termination.py:5

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_termination.py:6
# import tempfile
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_termination.py:6

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_termination.py:7
# import time
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_termination.py:7

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_termination.py:10
# from unittest import mock
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_termination.py:10

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_termination.py:12
# from arbol_trunk_trivial.termination import end_group
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_termination.py:12

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
