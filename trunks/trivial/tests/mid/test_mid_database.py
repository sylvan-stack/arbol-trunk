"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_database as _support
from test_database import (
    Address,
    DatabaseUnavailable,
    Limit,
    asyncio,
    conninfo,
    conninfo_to_dict,
    database,
    mock,
    os,
    postgres,
    psycopg,
    socket,
    tempfile,
    time,
    unittest,
)


class Address(_support.Address):
# TEST-TIER-BEGIN trunks/trivial/tests/test_database.py::Address.test_the_database_of_root_json_takes_the_place_of_any_the_address_names
    def test_the_database_of_root_json_takes_the_place_of_any_the_address_names(self) -> None:
        info = conninfo_to_dict(conninfo("postgresql://arbol@127.0.0.1:5432/other", "arbol_sapling", "secret"))
        self.assertEqual((info["host"], info["port"], info["user"], info["dbname"], info["password"]),
                         ("127.0.0.1", "5432", "arbol", "arbol_sapling", "secret"))
        self.assertEqual(info["connect_timeout"], "5")
        self.assertEqual(info["options"], "-c statement_timeout=5000")
# TEST-TIER-END trunks/trivial/tests/test_database.py::Address.test_the_database_of_root_json_takes_the_place_of_any_the_address_names

# TEST-TIER-BEGIN trunks/trivial/tests/test_database.py::Address.test_without_a_password_none_is_given
    def test_without_a_password_none_is_given(self) -> None:
        info = conninfo_to_dict(conninfo("postgresql://rct@%2Ftmp%2Frct-1a2b", "arbol_rct", None))
        self.assertEqual((info["host"], info["user"], info["dbname"]), ("/tmp/rct-1a2b", "rct", "arbol_rct"))
        self.assertNotIn("password", info)
# TEST-TIER-END trunks/trivial/tests/test_database.py::Address.test_without_a_password_none_is_given



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

# TEST-TIER-BEGIN trunks/trivial/tests/test_database.py::Limit.test_call_timeout_remains_five_seconds_when_scenario_time_is_divided
    def test_call_timeout_remains_five_seconds_when_scenario_time_is_divided(self) -> None:
        async def answer() -> int:
            return 42

        wait = asyncio.wait_for
        with mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "100"}), \
                mock.patch("arbol_trunk_trivial.database.asyncio.wait_for", wraps=wait) as limited:
            self.assertEqual(asyncio.run(database.within_limit(answer())), 42)
        self.assertEqual(limited.call_args.args[1], 5)
# TEST-TIER-END trunks/trivial/tests/test_database.py::Limit.test_call_timeout_remains_five_seconds_when_scenario_time_is_divided

# TEST-TIER-BEGIN trunks/trivial/tests/test_database.py::Limit.test_a_server_lost_at_commit_is_unavailable_and_transaction_commands_are_bounded
    def test_a_server_lost_at_commit_is_unavailable_and_transaction_commands_are_bounded(self) -> None:
        connection = mock.MagicMock()
        work = connection.transaction.return_value
        work.__aexit__.side_effect = psycopg.errors.ConnectionFailure("The server went away at commit.")

        async def transact() -> None:
            async with database.transaction(connection):
                pass

        wait = asyncio.wait_for
        with mock.patch("arbol_trunk_trivial.database.asyncio.wait_for", wraps=wait) as limited:
            with self.assertRaises(DatabaseUnavailable):
                asyncio.run(transact())
        self.assertEqual([call.args[1] for call in limited.call_args_list], [5, 5])
# TEST-TIER-END trunks/trivial/tests/test_database.py::Limit.test_a_server_lost_at_commit_is_unavailable_and_transaction_commands_are_bounded

# TEST-TIER-BEGIN trunks/trivial/tests/test_database.py::Limit.test_a_server_that_is_not_there_is_unavailable
    def test_a_server_that_is_not_there_is_unavailable(self) -> None:
        folder = tempfile.mkdtemp(prefix="trv-", dir="/tmp")
        self.addCleanup(os.rmdir, folder)
        connect = postgres(conninfo(f"postgresql://rct@{folder.replace('/', '%2F')}", "arbol_rct", None))
        with self.assertRaises(DatabaseUnavailable):
            asyncio.run(connect())
# TEST-TIER-END trunks/trivial/tests/test_database.py::Limit.test_a_server_that_is_not_there_is_unavailable
