"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_capabilities as _support
from test_capabilities import (CapabilityError ,CapabilityStopped ,DriverRun ,asyncio ,capability_query ,json ,os ,patch ,time)


class Capabilities(_support.Capabilities):


# TEST-TIER-BEGIN trunks/trivial/tests/test_capabilities.py::Capabilities.test_bounded_queries_stop_and_reap_without_inference
    def test_bounded_queries_stop_and_reap_without_inference(self) -> None:
        program = self.script("print('x' * 300000)\n")
        with self.assertRaises(CapabilityError):
            asyncio.run(capability_query(program, ["info"], str(self.home), lambda: False))
        program = self.script("import time\ntime.sleep(30)\n")
        started = time.monotonic()
        with self.assertRaises(CapabilityStopped):
            asyncio.run(capability_query(program, ["info"], str(self.home),
                                         lambda: time.monotonic() - started > 0.1))
        with patch("arbol_trunk_trivial.driver.CAPABILITY_SECONDS", 0.1), self.assertRaises(CapabilityError):
            asyncio.run(capability_query(program, ["info"], str(self.home), lambda: False))
        self.assertLess(time.monotonic() - started, 3)
# TEST-TIER-END trunks/trivial/tests/test_capabilities.py::Capabilities.test_bounded_queries_stop_and_reap_without_inference

# TEST-TIER-BEGIN trunks/trivial/tests/test_capabilities.py::Capabilities.test_capability_queries_and_the_run_launcher_stay_in_the_callers_process_group
    def test_capability_queries_and_the_run_launcher_stay_in_the_callers_process_group(self) -> None:
        program = self.script("import json,os\nprint(json.dumps({'pid':os.getpid(),'group':os.getpgrp()}))\n")
        query = asyncio.run(capability_query(program, ["info"], str(self.home), lambda: False))
        self.assertEqual(query['group'], os.getpgrp())
        self.assertNotEqual(query['pid'], os.getpid())

        async def start() -> dict[str, int]:
            request = self.home / 'request.json'
            request.write_text('{}')
            run = await DriverRun.start(program, request, str(self.home))
            output, _ = await run.process.communicate()
            result: dict[str, int] = json.loads(output)
            return result
        inference = asyncio.run(start())
        self.assertEqual(inference['group'], os.getpgrp())
        self.assertNotEqual(inference['pid'], os.getpid())
# TEST-TIER-END trunks/trivial/tests/test_capabilities.py::Capabilities.test_capability_queries_and_the_run_launcher_stay_in_the_callers_process_group
