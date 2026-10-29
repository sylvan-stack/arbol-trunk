"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_driver as _support
# from test_driver import (
#     LAUNCHER,
#     LONG,
#     Launcher,
#     Path,
#     Run,
#     launcher,
#     os,
#     tempfile,
#     unittest,
# )


# class Launcher(_support.Launcher):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_driver.py::Launcher.test_it_is_looked_for_only_in_the_folders_of_the_search_path
#     def test_it_is_looked_for_only_in_the_folders_of_the_search_path(self) -> None:
#         first, second = self.folder / "a", self.folder / "b"
#         first.mkdir()
#         second.mkdir()
#         launcher(second)
#         launcher(second, "arbol-codex-driver")
#         self.assertEqual(find_launcher("claude", f"{first}::{second}"), str(second / "arbol-claude-driver"))
#         self.assertEqual(find_launcher("codex", f"{first}:{second}"), str(second / "arbol-codex-driver"))
#         self.assertIsNone(find_launcher("cluade", f"{first}:{second}"))
#         self.assertIsNone(find_launcher("claude", str(first)))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_driver.py::Launcher.test_it_is_looked_for_only_in_the_folders_of_the_search_path

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_driver.py::Launcher.test_a_driver_with_a_slash_is_never_found
#     def test_a_driver_with_a_slash_is_never_found(self) -> None:
#         (self.folder / "arbol-x").mkdir()
#         launcher(self.folder / "arbol-x", "y-driver")
#         self.assertIsNone(find_launcher("x/y", str(self.folder)))
#         self.assertIsNone(find_launcher("../x", str(self.folder)))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_driver.py::Launcher.test_a_driver_with_a_slash_is_never_found



# class Run(_support.Run):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_driver.py::Run.test_it_starts_run_control_request_without_v_and_reads_every_event_line
#     def test_it_starts_run_control_request_without_v_and_reads_every_event_line(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             folder = Path(os.path.realpath(name))
#             program = launcher(folder)
#             request = folder / "run-1.json"
#             request.write_text("{}")
#
#             async def go() -> tuple[list[dict[str, object]], int]:
#                 run = await DriverRun.start(str(program), request, str(folder))
#                 events = []
#                 async for line in run.lines():
#                     events.append(line.event)
#                     if line.event["seq"] == 2:
#                         run.write_control('{"type":"stop"}')
#                         run.close_control()
#                 return events, await run.wait()
#
#             events, status = asyncio.run(go())
#             self.assertEqual(status, 0)
#             self.assertEqual([event["seq"] for event in events], [1, 2, 3])
#             self.assertEqual(events[1]["text"], LONG)
#             self.assertEqual((folder / "arguments").read_text().splitlines(),
#                              [str(program), "run", "--control", "--request", str(request)])
#             self.assertEqual((folder / "control").read_text(), '{"type":"stop"}\n')
#             group, cwd = (folder / "group").read_text().split()
#             self.assertEqual(int(group), os.getpgrp())
#             self.assertEqual(cwd, str(folder))
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_driver.py::Run.test_it_starts_run_control_request_without_v_and_reads_every_event_line

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_driver.py::Run.test_an_event_keeps_its_own_text
#     def test_an_event_keeps_its_own_text(self) -> None:
#         line = as_event(b'{"type":"text", "text":"a",  "seq":1}\r\n')
#         assert line is not None
#         self.assertEqual(line.text, '{"type":"text", "text":"a",  "seq":1}')
#         self.assertEqual(json.loads(line.text), line.event)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_driver.py::Run.test_an_event_keeps_its_own_text


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_driver.py:1
# import asyncio
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_driver.py:1

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_driver.py:2
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_driver.py:2

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_driver.py:8
# from arbol_trunk_trivial.driver import DriverRun, as_event, find_launcher
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_driver.py:8

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
