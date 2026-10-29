
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_driver.py::Launcher.test_it_is_looked_for_only_in_the_folders_of_the_search_path
# Reason: Path lookup and field-copy examples or ordinary transport round trips overlap actual shared scenarios and retained slow-reader control transport. Case reviewed: It is looked for only in the folders of the search path.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_driver.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_driver.py::Launcher.test_a_driver_with_a_slash_is_never_found
# Reason: Path lookup and field-copy examples or ordinary transport round trips overlap actual shared scenarios and retained slow-reader control transport. Case reviewed: A driver with a slash is never found.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_driver.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_driver_with_a_slash_is_never_found(self) -> None:
#         (self.folder / "arbol-x").mkdir()
#         launcher(self.folder / "arbol-x", "y-driver")
#         self.assertIsNone(find_launcher("x/y", str(self.folder)))
#         self.assertIsNone(find_launcher("../x", str(self.folder)))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_driver.py::Run.test_it_starts_run_control_request_without_v_and_reads_every_event_line
# Reason: Path lookup and field-copy examples or ordinary transport round trips overlap actual shared scenarios and retained slow-reader control transport. Case reviewed: It starts run control request without v and reads every event line.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_driver.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_driver.py::Run.test_an_event_keeps_its_own_text
# Reason: Path lookup and field-copy examples or ordinary transport round trips overlap actual shared scenarios and retained slow-reader control transport. Case reviewed: An event keeps its own text.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_driver.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_an_event_keeps_its_own_text(self) -> None:
#         line = as_event(b'{"type":"text", "text":"a",  "seq":1}\r\n')
#         assert line is not None
#         self.assertEqual(line.text, '{"type":"text", "text":"a",  "seq":1}')
#         self.assertEqual(json.loads(line.text), line.event)
# LOW-TIER-SOURCE-END
# LOW-TIER-END
