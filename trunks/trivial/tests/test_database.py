import asyncio
import os
import socket
import tempfile
import time
import unittest
from unittest import mock

import psycopg
from psycopg.conninfo import conninfo_to_dict

from arbol_trunk_trivial import database
from arbol_trunk_trivial.database import DatabaseUnavailable, conninfo, postgres


class Address(unittest.TestCase):
    def test_the_database_of_root_json_takes_the_place_of_any_the_address_names(self) -> None:
        info = conninfo_to_dict(conninfo("postgresql://arbol@127.0.0.1:5432/other", "arbol_sapling", "secret"))
        self.assertEqual((info["host"], info["port"], info["user"], info["dbname"], info["password"]),
                         ("127.0.0.1", "5432", "arbol", "arbol_sapling", "secret"))
        self.assertEqual(info["connect_timeout"], "5")
        self.assertEqual(info["options"], "-c statement_timeout=5000")

    def test_without_a_password_none_is_given(self) -> None:
        info = conninfo_to_dict(conninfo("postgresql://rct@%2Ftmp%2Frct-1a2b", "arbol_rct", None))
        self.assertEqual((info["host"], info["user"], info["dbname"]), ("/tmp/rct-1a2b", "rct", "arbol_rct"))
        self.assertNotIn("password", info)


class Limit(unittest.TestCase):
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

    def test_call_timeout_remains_five_seconds_when_scenario_time_is_divided(self) -> None:
        async def answer() -> int:
            return 42

        wait = asyncio.wait_for
        with mock.patch.dict("os.environ", {"ARBOL_TEST_TIME_SCALE": "100"}), \
                mock.patch("arbol_trunk_trivial.database.asyncio.wait_for", wraps=wait) as limited:
            self.assertEqual(asyncio.run(database.within_limit(answer())), 42)
        self.assertEqual(limited.call_args.args[1], 5)

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

    def test_a_server_that_is_not_there_is_unavailable(self) -> None:
        folder = tempfile.mkdtemp(prefix="trv-", dir="/tmp")
        self.addCleanup(os.rmdir, folder)
        connect = postgres(conninfo(f"postgresql://rct@{folder.replace('/', '%2F')}", "arbol_rct", None))
        with self.assertRaises(DatabaseUnavailable):
            asyncio.run(connect())


if __name__ == "__main__":
    unittest.main()
