
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_live_build.py::LiveCheck.test_the_unsigned_standin_fails_live_and_the_fixture_is_closed
# Reason: Mocked qualification rows and simple bridge/cleanup branches duplicate the retained actual live qualification entry point; they do not independently qualify a live Build. Case reviewed: The unsigned standin fails live and the fixture is closed.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_live_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_live_build.py::LiveCheck.test_a_timeout_or_launcher_failure_also_closes_the_fixture
# Reason: Mocked qualification rows and simple bridge/cleanup branches duplicate the retained actual live qualification entry point; they do not independently qualify a live Build. Case reviewed: A timeout or launcher failure also closes the fixture.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_live_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_live_build.py::LiveCheck.test_success_requires_the_completed_exchange_answer_and_test_subscription_usage
# Reason: Mocked qualification rows and simple bridge/cleanup branches duplicate the retained actual live qualification entry point; they do not independently qualify a live Build. Case reviewed: Success requires the completed exchange answer and test subscription usage.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_live_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_live_build.py::LiveCheck.test_usage_from_another_subscription_cannot_qualify_the_build
# Reason: Mocked qualification rows and simple bridge/cleanup branches duplicate the retained actual live qualification entry point; they do not independently qualify a live Build. Case reviewed: Usage from another subscription cannot qualify the build.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_live_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_usage_from_another_subscription_cannot_qualify_the_build(self) -> None:
#         self.fixture.run.return_value = SimpleNamespace(status=0, output=[])
#         self.fixture.rows.side_effect = [[{"state": "completed"}], [{"role": "assistant"}],
#                                          [{"kind": "agent", "outcome": "completed", "usage": {"inputTokens": 7},
#                                            "started": {"subscriptionId": "anthropic"}}]]
#         with self.assertRaisesRegex(ValueError, "test-account"):
#             live(self.base, owner=self.owner)
#         self.fixture.close.assert_called_once()
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_live_build.py::LiveCheck.test_relative_or_empty_test_state_is_refused_before_setup
# Reason: Mocked qualification rows and simple bridge/cleanup branches duplicate the retained actual live qualification entry point; they do not independently qualify a live Build. Case reviewed: Relative or empty test state is refused before setup.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_live_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_relative_or_empty_test_state_is_refused_before_setup(self) -> None:
#         for state in ("", "relative"):
#             with self.subTest(state=state), mock.patch.dict(os.environ, {"ARBOL_BUILD_TEST_STATE_DIR": state}):
#                 with self.assertRaisesRegex(ValueError, "absolute test state"):
#                     live(self.base, owner=self.owner)
#         self.factory.assert_not_called()
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_live_build.py::LiveCheck.test_the_bridge_keeps_arguments_and_executes_the_installed_driver
# Reason: Mocked qualification rows and simple bridge/cleanup branches duplicate the retained actual live qualification entry point; they do not independently qualify a live Build. Case reviewed: The bridge keeps arguments and executes the installed driver.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_live_build.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_bridge_keeps_arguments_and_executes_the_installed_driver(self) -> None:
#         launcher = self.base / "bridge"
#         driver_bridge(launcher, self.owner, self.state)
#         subprocess.run([str(launcher), "subscriptions", "list", "two words", ""], check=False, timeout=10,
#                        capture_output=True)
#         self.assertEqual(self.report.read_text().splitlines()[4:], ["subscriptions", "list", "two words", ""])
# LOW-TIER-SOURCE-END
# LOW-TIER-END
