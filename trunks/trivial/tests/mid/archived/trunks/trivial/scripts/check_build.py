# Mid-tier source from trunks/trivial/scripts/check_build.py; see MID_TIER.md.
# Shared helpers and refusal entry points remain at the original path.

# TEST-TIER-DISABLED-BEGIN trunks/trivial/scripts/check_build.py::unit
# def unit(folder: Path) -> int:
#     sys.path.insert(0, str(folder))
#     sys.path.insert(0, str(folder / "src"))
#     suite = unittest.TestLoader().discover(str(folder / "tests"))
#     if suite.countTestCases() == 0:
#         raise ValueError("The packaged unit suite has no tests.")
#     return 0 if unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful() else 1
# TEST-TIER-DISABLED-END trunks/trivial/scripts/check_build.py::unit

# TEST-TIER-DISABLED-BEGIN trunks/trivial/scripts/check_build.py::live
# def live(folder: Path, *, owner: Path | None = None) -> int:
#     owner = owner or Path(pwd.getpwuid(os.getuid()).pw_dir)
#     state_text = os.environ.get("ARBOL_BUILD_TEST_STATE_DIR",
#                                 str(owner / "Library/Application Support/Arbol/drivers/arbol-claude-driver"))
#     if not state_text or not Path(state_text).is_absolute():
#         raise ValueError("live: ARBOL_BUILD_TEST_STATE_DIR must be an absolute test state directory.")
#     fixture = live_fixture(folder, owner)
#     try:
#         driver_bridge(fixture.standin / "bin/arbol-claude-driver", owner, Path(state_text))
#         result = fixture.run(["run", "--driver", "claude", "--subscription", "test-anthropic", "--model", "haiku",
#                               "Answer with the single word: ready"], scale=None, seconds=300)
#         if result.status != 0:
#             print(json.dumps({"check": "live", "passed": False, "exitStatus": result.status,
#                               "output": result.output}), flush=True)
#             return 1
#         exchanges = fixture.rows("SELECT id, state, build, route FROM exchanges")
#         messages = fixture.rows("SELECT role, text FROM messages WHERE role = 'assistant'")
#         runs = fixture.rows("SELECT kind, outcome, usage, started FROM runs")
#         if (len(exchanges) != 1 or exchanges[0]["state"] != "completed" or not messages
#                 or len(runs) != 1 or runs[0]["kind"] != "agent" or runs[0]["outcome"] != "completed"
#                 or not runs[0]["usage"] or not isinstance(runs[0]["started"], dict)
#                 or runs[0]["started"].get("subscriptionId") != "test-anthropic"):
#             raise ValueError("live: the completed Exchange, assistant answer or test-account run and usage are missing.")
#         print(json.dumps({"check": "live", "passed": True, "exchange": exchanges[0]["id"],
#                           "build": exchanges[0]["build"], "subscription": "test-anthropic", "model": "haiku",
#                           "usage": runs[0]["usage"]}), flush=True)
#         return 0
#     finally:
#         fixture.close()
# TEST-TIER-DISABLED-END trunks/trivial/scripts/check_build.py::live

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/scripts/check_build.py:10
# import pwd
# TEST-TIER-IMPORTS-END trunks/trivial/scripts/check_build.py:10

# TEST-TIER-IMPORTS-BEGIN trunks/trivial/scripts/check_build.py:14
# import unittest
# TEST-TIER-IMPORTS-END trunks/trivial/scripts/check_build.py:14

raise RuntimeError("Mid-tier checks require an explicitly requested testing task; see MID_TIER.md.")
