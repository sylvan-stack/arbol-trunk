"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_capabilities as _support
# from test_capabilities import (
#     Capabilities,
#     Path,
#     asyncio,
#     capabilities,
#     shlex,
#     sys,
#     tempfile,
#     unittest,
# )


# class Capabilities(_support.Capabilities):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_capabilities.py::Capabilities.test_contracts_and_selected_families_fail_closed
#     def test_contracts_and_selected_families_fail_closed(self) -> None:
#         for contract in (1, 2):
#             self.fixture(contract=contract)
#             self.check()
#             self.check(subscription=None)
#         for invalid_contract in (0, 3, True, "2", None):
#             self.fixture(contract=invalid_contract)
#             with self.assertRaises(CapabilityError):
#                 self.check()
#         self.fixture(family="retired")
#         with self.assertRaises(CapabilityError):
#             self.check()
#         self.fixture()
#         for driver, selected in (("claude", "test-zai"), ("pi", "missing")):
#             with self.assertRaises(CapabilityError):
#                 self.check(driver, selected)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_capabilities.py::Capabilities.test_contracts_and_selected_families_fail_closed

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_capabilities.py::Capabilities.test_pending_migration_blocks_both_old_and_new_routes_until_explicit_restore
#     def test_pending_migration_blocks_both_old_and_new_routes_until_explicit_restore(self) -> None:
#         path = self.home / ".arbol/pi-cutover.json"
#         path.parent.mkdir()
#         for phase in ("preparing", "quiesced", "publishing", "verifying", "restoring", "complete", "restored"):
#             path.write_text(json.dumps({"phase": phase, "blockedRoutes": [
#                 {"driver": "claude", "subscription": "zai"}, {"driver": "pi", "subscription": "test-zai"}]}))
#             migration_ready(self.home, "claude", "anthropic")
#             for driver, subscription in (("claude", "zai"), ("pi", "test-zai"), ("claude", None)):
#                 if phase in ("complete", "restored"):
#                     migration_ready(self.home, driver, subscription)
#                 else:
#                     with self.assertRaises(CapabilityError):
#                         migration_ready(self.home, driver, subscription)
#         path.write_text("{")
#         with self.assertRaises(CapabilityError):
#             migration_ready(self.home, "pi", "test-zai")
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_capabilities.py::Capabilities.test_pending_migration_blocks_both_old_and_new_routes_until_explicit_restore

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_capabilities.py::Capabilities.test_bounded_queries_stop_and_reap_without_inference
#     def test_bounded_queries_stop_and_reap_without_inference(self) -> None:
#         program = self.script("print('x' * 300000)\n")
#         with self.assertRaises(CapabilityError):
#             asyncio.run(capability_query(program, ["info"], str(self.home), lambda: False))
#         program = self.script("import time\ntime.sleep(30)\n")
#         started = time.monotonic()
#         with self.assertRaises(CapabilityStopped):
#             asyncio.run(capability_query(program, ["info"], str(self.home),
#                                          lambda: time.monotonic() - started > 0.1))
#         with patch("arbol_trunk_trivial.driver.CAPABILITY_SECONDS", 0.1), self.assertRaises(CapabilityError):
#             asyncio.run(capability_query(program, ["info"], str(self.home), lambda: False))
#         self.assertLess(time.monotonic() - started, 3)
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_capabilities.py::Capabilities.test_bounded_queries_stop_and_reap_without_inference

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_capabilities.py::Capabilities.test_capability_queries_and_the_run_launcher_stay_in_the_callers_process_group
#     def test_capability_queries_and_the_run_launcher_stay_in_the_callers_process_group(self) -> None:
#         program = self.script("import json,os\nprint(json.dumps({'pid':os.getpid(),'group':os.getpgrp()}))\n")
#         query = asyncio.run(capability_query(program, ["info"], str(self.home), lambda: False))
#         self.assertEqual(query['group'], os.getpgrp())
#         self.assertNotEqual(query['pid'], os.getpid())
#
#         async def start() -> dict[str, int]:
#             request = self.home / 'request.json'
#             request.write_text('{}')
#             run = await DriverRun.start(program, request, str(self.home))
#             output, _ = await run.process.communicate()
#             result: dict[str, int] = json.loads(output)
#             return result
#         inference = asyncio.run(start())
#         self.assertEqual(inference['group'], os.getpgrp())
#         self.assertNotEqual(inference['pid'], os.getpid())
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_capabilities.py::Capabilities.test_capability_queries_and_the_run_launcher_stay_in_the_callers_process_group


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_capabilities.py:2
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_capabilities.py:2

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_capabilities.py:3
# import os
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_capabilities.py:3

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_capabilities.py:7
# import time
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_capabilities.py:7

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_capabilities.py:10
# from unittest.mock import patch
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_capabilities.py:10

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_capabilities.py:12
# from arbol_trunk_trivial.driver import (
#     CapabilityError,
#     CapabilityStopped,
#     DriverRun,
#     capabilities,
#     capability_query,
#     migration_ready,
# )
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_capabilities.py:12

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
