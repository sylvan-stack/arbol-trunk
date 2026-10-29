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
