"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_loop as _support
from test_loop import (DriverRun ,FakeDatabase ,RowMaker ,RunOver ,SLOW_READER ,Saver ,append ,asyncio ,drive ,event ,finished ,os ,time)


class SilentRuns(_support.SilentRuns):

# TEST-TIER-BEGIN trunks/trivial/tests/test_loop.py::SilentRuns.test_every_event_resets_silence_even_when_its_tool_output_is_omitted
    def test_every_event_resets_silence_even_when_its_tool_output_is_omitted(self) -> None:
        self.events.tool_bytes[("x.1", "c")] = 1024 * 1024 + 1
        self.driver.at(0, "event", event(1, "started"))
        self.driver.at(900, "event", event(2, "tool_output_delta", callId="c", text="still alive"))
        self.driver.at(1859, "event", finished(3))
        self.driver.at(1860, "exit", 0)
        over = self.drive()
        self.assertFalse(over.silent)
        self.assertEqual(self.driver.control, [])
        self.assertEqual([line["event"]["type"] for line in self.lines()], ["started", "finished"])
# TEST-TIER-END trunks/trivial/tests/test_loop.py::SilentRuns.test_every_event_resets_silence_even_when_its_tool_output_is_omitted


class HandingOn(_support.HandingOn):
# TEST-TIER-BEGIN trunks/trivial/tests/test_loop.py::HandingOn.test_each_line_goes_unchanged_to_the_control_input_and_what_the_driver_has_not_taken_waits_in_order
    def test_each_line_goes_unchanged_to_the_control_input_and_what_the_driver_has_not_taken_waits_in_order(
            self) -> None:
        lines = ['{"type":"answer","askId":"ask_1","answer":{"type":"answers","answers":{"q":["%s"]}}}' % (str(i) * 60000)
                 for i in range(2)] + ['{ "type" : "stop" }']
        for line in lines:
            append(self.folder / "control", line)
        launcher = self.folder / "arbol-claude-driver"
        launcher.write_text(SLOW_READER)
        os.chmod(launcher, 0o755)
        (self.folder / "run-1.json").write_text("{}")
        writes: list[float] = []

        async def go() -> RunOver:
            run = await DriverRun.start(str(launcher), self.folder / "run-1.json", str(self.folder))
            write = run.write_control

            def timed(line: str) -> bool:
                began = time.monotonic()
                handed = write(line)
                writes.append(time.monotonic() - began)
                return handed

            run.write_control = timed  # type: ignore[method-assign]
            over = await drive(run, self.events, RowMaker("x"), Saver(FakeDatabase().connect()), self.control)
            await run.wait()
            return over

        over = asyncio.run(go())
        self.assertEqual(over.finished["seq"] if over.finished else None, 2)
        self.assertEqual((self.folder / "received").read_text(), "".join(line + "\n" for line in lines))
        self.assertEqual(len(writes), 3)
        self.assertLess(max(writes), 0.05)
# TEST-TIER-END trunks/trivial/tests/test_loop.py::HandingOn.test_each_line_goes_unchanged_to_the_control_input_and_what_the_driver_has_not_taken_waits_in_order
