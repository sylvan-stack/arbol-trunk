"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_live_build as _support
# from test_live_build import (
#     LiveCheck,
#     Path,
#     contextlib,
#     io,
#     mock,
#     os,
#     shlex,
#     tempfile,
#     unittest,
# )


# class LiveCheck(_support.LiveCheck):
# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_live_build.py::LiveCheck.test_the_unsigned_standin_fails_live_and_the_fixture_is_closed
#     def test_the_unsigned_standin_fails_live_and_the_fixture_is_closed(self) -> None:
#         def unsigned(args: list[str], **kwargs: object) -> SimpleNamespace:
#             self.assertEqual(args, ["run", "--driver", "claude", "--subscription", "test-anthropic", "--model",
#                                     "haiku", "Answer with the single word: ready"])
#             self.assertEqual(kwargs, {"scale": None, "seconds": 300})
#             result = subprocess.run([str(self.fixture.standin / "bin/arbol-claude-driver"), *args],
#                                     env={"HOME": str(self.fixture.home), "PATH": "/usr/bin:/bin", "LANG": "C"},
#                                     capture_output=True, text=True, timeout=10)
#             return SimpleNamespace(status=result.returncode, output=[json.loads(result.stdout)])
#         self.fixture.run.side_effect = unsigned
#         self.assertEqual(live(self.base, owner=self.owner), 1)
#         self.fixture.close.assert_called_once()
#         result = json.loads(self.output.getvalue())
#         self.assertEqual((result["check"], result["passed"], result["output"][0]["error"]["code"]),
#                          ("live", False, "not_signed_in"))
#         report = self.report.read_text().splitlines()
#         self.assertEqual(report[:4], [str(self.owner), str(self.owner / ".local/bin") + ":/usr/bin:/bin:/usr/sbin:/sbin",
#                                      "--state-dir", str(self.state)])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_live_build.py::LiveCheck.test_the_unsigned_standin_fails_live_and_the_fixture_is_closed

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_live_build.py::LiveCheck.test_a_timeout_or_launcher_failure_also_closes_the_fixture
#     def test_a_timeout_or_launcher_failure_also_closes_the_fixture(self) -> None:
#         self.fixture.run.side_effect = subprocess.TimeoutExpired("trunk", 300)
#         with self.assertRaises(subprocess.TimeoutExpired):
#             live(self.base, owner=self.owner)
#         self.fixture.close.assert_called_once()
#         self.fixture.close.reset_mock()
#         self.driver.unlink()
#         with self.assertRaisesRegex(ValueError, "installed Claude Driver"):
#             live(self.base, owner=self.owner)
#         self.fixture.close.assert_called_once()
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_live_build.py::LiveCheck.test_a_timeout_or_launcher_failure_also_closes_the_fixture

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_live_build.py::LiveCheck.test_success_requires_the_completed_exchange_answer_and_test_subscription_usage
#     def test_success_requires_the_completed_exchange_answer_and_test_subscription_usage(self) -> None:
#         self.fixture.run.return_value = SimpleNamespace(status=0, output=[])
#         self.fixture.rows.side_effect = [[{"id": "exchange", "state": "completed", "build": "a"}],
#                                          [{"role": "assistant", "text": "ready"}],
#                                          [{"kind": "agent", "outcome": "completed", "usage": {"inputTokens": 7},
#                                            "started": {"subscriptionId": "test-anthropic"}}]]
#         self.assertEqual(live(self.base, owner=self.owner), 0)
#         result = json.loads(self.output.getvalue())
#         self.assertEqual((result["check"], result["passed"], result["usage"]),
#                          ("live", True, {"inputTokens": 7}))
#         self.fixture.close.assert_called_once()
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_live_build.py::LiveCheck.test_success_requires_the_completed_exchange_answer_and_test_subscription_usage

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_live_build.py::LiveCheck.test_usage_from_another_subscription_cannot_qualify_the_build
#     def test_usage_from_another_subscription_cannot_qualify_the_build(self) -> None:
#         self.fixture.run.return_value = SimpleNamespace(status=0, output=[])
#         self.fixture.rows.side_effect = [[{"state": "completed"}], [{"role": "assistant"}],
#                                          [{"kind": "agent", "outcome": "completed", "usage": {"inputTokens": 7},
#                                            "started": {"subscriptionId": "anthropic"}}]]
#         with self.assertRaisesRegex(ValueError, "test-account"):
#             live(self.base, owner=self.owner)
#         self.fixture.close.assert_called_once()
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_live_build.py::LiveCheck.test_usage_from_another_subscription_cannot_qualify_the_build

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_live_build.py::LiveCheck.test_relative_or_empty_test_state_is_refused_before_setup
#     def test_relative_or_empty_test_state_is_refused_before_setup(self) -> None:
#         for state in ("", "relative"):
#             with self.subTest(state=state), mock.patch.dict(os.environ, {"ARBOL_BUILD_TEST_STATE_DIR": state}):
#                 with self.assertRaisesRegex(ValueError, "absolute test state"):
#                     live(self.base, owner=self.owner)
#         self.factory.assert_not_called()
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_live_build.py::LiveCheck.test_relative_or_empty_test_state_is_refused_before_setup

# TEST-TIER-DISABLED-BEGIN trunks/trivial/tests/test_live_build.py::LiveCheck.test_the_bridge_keeps_arguments_and_executes_the_installed_driver
#     def test_the_bridge_keeps_arguments_and_executes_the_installed_driver(self) -> None:
#         launcher = self.base / "bridge"
#         driver_bridge(launcher, self.owner, self.state)
#         subprocess.run([str(launcher), "subscriptions", "list", "two words", ""], check=False, timeout=10,
#                        capture_output=True)
#         self.assertEqual(self.report.read_text().splitlines()[4:], ["subscriptions", "list", "two words", ""])
# TEST-TIER-DISABLED-END trunks/trivial/tests/test_live_build.py::LiveCheck.test_the_bridge_keeps_arguments_and_executes_the_installed_driver


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_live_build.py:3
# import json
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_live_build.py:3

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_live_build.py:6
# import subprocess
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_live_build.py:6

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_live_build.py:10
# from types import SimpleNamespace
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_live_build.py:10

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/tests/test_live_build.py:13
# from scripts.check_build import driver_bridge, live
# TEST-TIER-IMPORTS-END trunks/trivial/tests/test_live_build.py:13

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
