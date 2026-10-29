"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_database as _support
from test_database import (DatabaseUnavailable ,asyncio ,conninfo ,database ,mock ,os ,postgres ,socket ,tempfile ,time)


class Limit(_support.Limit):
# TEST-TIER-BEGIN trunks/trivial/tests/test_database.py::Limit.test_a_server_that_never_answers_is_given_up_after_the_limit
    def test_a_server_that_never_answers_is_given_up_after_the_limit(self) -> None:
        folder = tempfile.mkdtemp(prefix="trv-", dir="/tmp")
        self.addCleanup(os.rmdir, folder)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        path = os.path.join(folder, ".s.PGSQL.5432")
        listener.bind(path)
        self.addCleanup(os.unlink, path)
        self.addCleanup(listener.close)
        listener.listen(1)
        connect = postgres(conninfo(f"postgresql://rct@{folder.replace('/', '%2F')}", "arbol_rct", None))
        with mock.patch.object(database, "CALL_SECONDS", 0.3):
            began = time.monotonic()
            with self.assertRaises(DatabaseUnavailable):
                asyncio.run(connect())
            self.assertLess(time.monotonic() - began, 3)
# TEST-TIER-END trunks/trivial/tests/test_database.py::Limit.test_a_server_that_never_answers_is_given_up_after_the_limit

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_database.py::Address.test_the_database_of_root_json_takes_the_place_of_any_the_address_names
# Reason: Connection-string/status/timeout-argument tables mirror readable branches; retain the actual nonresponsive socket boundary. Case reviewed: The database of root json takes the place of any the address names.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_database.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_database_of_root_json_takes_the_place_of_any_the_address_names(self) -> None:
#         info = conninfo_to_dict(conninfo("postgresql://arbol@127.0.0.1:5432/other", "arbol_sapling", "secret"))
#         self.assertEqual((info["host"], info["port"], info["user"], info["dbname"], info["password"]),
#                          ("127.0.0.1", "5432", "arbol", "arbol_sapling", "secret"))
#         self.assertEqual(info["connect_timeout"], "5")
#         self.assertEqual(info["options"], "-c statement_timeout=5000")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_database.py::Address.test_without_a_password_none_is_given
# Reason: Connection-string/status/timeout-argument tables mirror readable branches; retain the actual nonresponsive socket boundary. Case reviewed: Without a password none is given.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_database.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_without_a_password_none_is_given(self) -> None:
#         info = conninfo_to_dict(conninfo("postgresql://rct@%2Ftmp%2Frct-1a2b", "arbol_rct", None))
#         self.assertEqual((info["host"], info["user"], info["dbname"]), ("/tmp/rct-1a2b", "rct", "arbol_rct"))
#         self.assertNotIn("password", info)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_database.py::Limit.test_call_timeout_remains_five_seconds_when_scenario_time_is_divided
# Reason: Connection-string/status/timeout-argument tables mirror readable branches; retain the actual nonresponsive socket boundary. Case reviewed: Call timeout remains five seconds when scenario time is divided.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_database.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_call_timeout_remains_five_seconds_when_scenario_time_is_divided(self) -> None:
#         async def answer() -> int:
#             return 42
#
#         wait = asyncio.wait_for
#         with mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "100"}), \
#                 mock.patch("arbol_trunk_trivial.database.asyncio.wait_for", wraps=wait) as limited:
#             self.assertEqual(asyncio.run(database.within_limit(answer())), 42)
#         self.assertEqual(limited.call_args.args[1], 5)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_database.py::Limit.test_a_server_lost_at_commit_is_unavailable_and_transaction_commands_are_bounded
# Reason: Connection-string/status/timeout-argument tables mirror readable branches; retain the actual nonresponsive socket boundary. Case reviewed: A server lost at commit is unavailable and transaction commands are bounded.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_database.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_server_lost_at_commit_is_unavailable_and_transaction_commands_are_bounded(self) -> None:
#         connection = mock.MagicMock()
#         work = connection.transaction.return_value
#         work.__aexit__.side_effect = psycopg.errors.ConnectionFailure("The server went away at commit.")
#
#         async def transact() -> None:
#             async with database.transaction(connection):
#                 pass
#
#         wait = asyncio.wait_for
#         with mock.patch("arbol_trunk_trivial.database.asyncio.wait_for", wraps=wait) as limited:
#             with self.assertRaises(DatabaseUnavailable):
#                 asyncio.run(transact())
#         self.assertEqual([call.args[1] for call in limited.call_args_list], [5, 5])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: trunks/trivial/tests/mid/test_mid_database.py::Limit.test_a_server_that_is_not_there_is_unavailable
# Reason: Connection-string/status/timeout-argument tables mirror readable branches; retain the actual nonresponsive socket boundary. Case reviewed: A server that is not there is unavailable.
# Source: arbol-trunk@d05362c865f8aea86b162c1f7a275c552f48ed43:trunks/trivial/tests/mid/test_mid_database.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_server_that_is_not_there_is_unavailable(self) -> None:
#         folder = tempfile.mkdtemp(prefix="trv-", dir="/tmp")
#         self.addCleanup(os.rmdir, folder)
#         connect = postgres(conninfo(f"postgresql://rct@{folder.replace('/', '%2F')}", "arbol_rct", None))
#         with self.assertRaises(DatabaseUnavailable):
#             asyncio.run(connect())
# LOW-TIER-SOURCE-END
# LOW-TIER-END
