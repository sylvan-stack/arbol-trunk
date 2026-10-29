"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_repeat as _support
from test_repeat import (
    Acceptance,
    AcceptanceHome,
    Accepted,
    CHAT,
    DuplicateExchange,
    Exchange,
    ExchangeFolder,
    FakeConnection,
    FakeDatabase,
    Output,
    Path,
    PriorExchange,
    Refusal,
    Repeated,
    Repeats,
    X,
    accept_message,
    asyncio,
    copy,
    json,
    mock,
    os,
    root_lock,
    run_exchange,
    started_at,
    subprocess,
    sys,
    time,
)


class Repeats(_support.Repeats):
# TEST-TIER-BEGIN trunks/trivial/tests/test_repeat.py::Repeats.test_a_repeat_returns_the_original_acceptance_before_making_any_identifier
    def test_a_repeat_returns_the_original_acceptance_before_making_any_identifier(self) -> None:
        database = FakeDatabase()
        first = self.accept(database, "--exchange", X, "--chat", CHAT, "original")
        database.exchanges[X].state = "completed"
        database.exchanges[X].trunk, database.exchanges[X].build = "another", "abc"
        before = copy.deepcopy((database.chats, database.exchanges, database.messages))
        with mock.patch("arbol_trunk_trivial.accept.uuid.uuid4", side_effect=AssertionError("An identifier was made")):
            with self.assertRaises(Repeated) as caught:
                self.accept(database, "--exchange", X, "changed input")
        line = json.loads(caught.exception.line)
        self.assertEqual((line["duplicate"], line["exchange"], line["chat"], line["number"], line["trunk"], line["build"]),
                         (True, X, CHAT, 1, "another", "abc"))
        self.assertEqual((database.chats, database.exchanges, database.messages), before)
        self.assertTrue(first.folder.path.exists())
# TEST-TIER-END trunks/trivial/tests/test_repeat.py::Repeats.test_a_repeat_returns_the_original_acceptance_before_making_any_identifier

# TEST-TIER-BEGIN trunks/trivial/tests/test_repeat.py::Repeats.test_a_repeat_in_the_database_is_found_at_the_insert_race_too
    def test_a_repeat_in_the_database_is_found_at_the_insert_race_too(self) -> None:
        database = FakeDatabase()

        async def raced(connection: FakeConnection, value: Acceptance) -> Accepted:
            raise DuplicateExchange(PriorExchange(X, CHAT, 1, "trivial", "f"))

        with mock.patch.object(FakeConnection, "accept", raced), self.assertRaises(Repeated) as caught:
            self.accept(database, "--exchange", X, "hello")
        self.assertEqual(json.loads(caught.exception.line)["build"], "f")
        self.assertEqual(list(self.exchanges.iterdir()), [])
# TEST-TIER-END trunks/trivial/tests/test_repeat.py::Repeats.test_a_repeat_in_the_database_is_found_at_the_insert_race_too

# TEST-TIER-BEGIN trunks/trivial/tests/test_repeat.py::Repeats.test_a_repeat_from_run_has_only_its_acceptance_and_exit_status_zero
    def test_a_repeat_from_run_has_only_its_acceptance_and_exit_status_zero(self) -> None:
        database = FakeDatabase()
        first = self.accept(database, "--exchange", X, "hello")
        lines: list[str] = []
        prepared = self.prepared("--driver", "claude", "--exchange", X, "hello")
        status = asyncio.run(run_exchange(prepared, database.connect(), build="0", process={},
                                           started=time.monotonic(), output=Output(lines.append), search_path=""))
        self.assertEqual(status, 0)
        self.assertEqual(len(lines), 1)
        self.assertTrue(json.loads(lines[0])["duplicate"])
        self.assertFalse((first.folder.path / "run-1.json").exists())
# TEST-TIER-END trunks/trivial/tests/test_repeat.py::Repeats.test_a_repeat_from_run_has_only_its_acceptance_and_exit_status_zero

# TEST-TIER-BEGIN trunks/trivial/tests/test_repeat.py::Repeats.test_an_old_unaccepted_folder_of_a_dead_start_is_reclaimed
    def test_an_old_unaccepted_folder_of_a_dead_start_is_reclaimed(self) -> None:
        for dot in (False, True):
            with self.subTest(dot=dot):
                self.abandoned(dot=dot)
                database = FakeDatabase()
                with mock.patch("arbol_trunk_trivial.claim.time.time", return_value=time.time() + 30):
                    accepted = self.accept(database, "--exchange", X, "new message")
                self.assertEqual(database.messages[(X, 0)], ("user", "new message"))
                self.assertEqual(sorted(p.name for p in self.exchanges.iterdir()), [X])
                accepted.folder.discard()
# TEST-TIER-END trunks/trivial/tests/test_repeat.py::Repeats.test_an_old_unaccepted_folder_of_a_dead_start_is_reclaimed

# TEST-TIER-BEGIN trunks/trivial/tests/test_repeat.py::Repeats.test_a_young_folder_or_an_old_folder_of_a_living_start_is_preserved
    def test_a_young_folder_or_an_old_folder_of_a_living_start_is_preserved(self) -> None:
        folder = self.abandoned()
        before = (folder.path / "record.json").read_bytes()
        with self.assertRaises(Refusal) as caught:
            self.accept(FakeDatabase(), "--exchange", X, "hello")
        self.assertEqual(caught.exception.code, "in_progress")
        self.assertEqual((folder.path / "record.json").read_bytes(), before)
        folder.discard()
        folder = self.abandoned(live=True)
        with (mock.patch("arbol_trunk_trivial.claim.time.time", return_value=time.time() + 30),
              self.assertRaises(Refusal) as caught):
            self.accept(FakeDatabase(), "--exchange", X, "hello")
        self.assertEqual(caught.exception.code, "in_progress")
        self.assertTrue(folder.path.exists())
# TEST-TIER-END trunks/trivial/tests/test_repeat.py::Repeats.test_a_young_folder_or_an_old_folder_of_a_living_start_is_preserved

# TEST-TIER-BEGIN trunks/trivial/tests/test_repeat.py::Repeats.test_two_starts_of_one_identifier_leave_only_the_winners_folder_and_acceptance
    def test_two_starts_of_one_identifier_leave_only_the_winners_folder_and_acceptance(self) -> None:
        async def race() -> None:
            database = FakeDatabase()
            accepting, release = asyncio.Event(), asyncio.Event()
            original = FakeConnection.accept
            calls = 0

            async def held(connection: FakeConnection, value: Acceptance) -> Accepted:
                nonlocal calls
                calls += 1
                accepting.set()
                await release.wait()
                return await original(connection, value)

            async def start(message: str) -> Exchange:
                return await accept_message(self.prepared("--driver", "claude", "--exchange", X, message),
                                            database.connect(), build="0",
                                            process={"pid": os.getpid(), "startedAt": started_at()},
                                            started=time.monotonic())

            with mock.patch.object(FakeConnection, "accept", held):
                first = asyncio.create_task(start("winner"))
                try:
                    await asyncio.wait_for(accepting.wait(), 2)
                    before = (self.exchanges / X / "record.json").read_bytes()
                    with self.assertRaises(Refusal) as caught:
                        await start("loser")
                    self.assertEqual(caught.exception.code, "in_progress")
                    self.assertEqual((self.exchanges / X / "record.json").read_bytes(), before)
                    self.assertEqual(database.exchanges, {})
                finally:
                    release.set()
                    winner = await first
            self.assertEqual(calls, 1)
            self.assertEqual(list(database.exchanges), [X])
            self.assertEqual(database.messages[(X, 0)], ("user", "winner"))
            self.assertEqual(sorted(p.name for p in self.exchanges.iterdir()), [X])
            await winner.connection.close()
        asyncio.run(race())
# TEST-TIER-END trunks/trivial/tests/test_repeat.py::Repeats.test_two_starts_of_one_identifier_leave_only_the_winners_folder_and_acceptance

# TEST-TIER-BEGIN trunks/trivial/tests/test_repeat.py::Repeats.test_another_process_cannot_claim_while_the_root_is_locked_and_its_wait_is_bounded
    def test_another_process_cannot_claim_while_the_root_is_locked_and_its_wait_is_bounded(self) -> None:
        code = """
import asyncio,sys,time
from pathlib import Path
from arbol_trunk_trivial.claim import claim_folder
from arbol_trunk_trivial.errors import Refusal
async def main():
    try:
        await claim_folder(Path(sys.argv[1]), sys.argv[2], {}, time.monotonic()+0.05)
    except Refusal as error:
        print(error.code)
    else:
        print("claimed")
asyncio.run(main())
"""
        source = Path(_support.__file__).resolve().parents[1] / "src"
        code = f"import sys; sys.path.insert(0, {str(source)!r})\n" + code
        async def check() -> None:
            async with root_lock(self.exchanges, time.monotonic() + 1):
                result = await asyncio.to_thread(subprocess.run, [sys.executable, "-I", "-B", "-c", code,
                                                                  str(self.exchanges), X],
                                                  capture_output=True, text=True, timeout=5, check=True)
                self.assertEqual(result.stdout.strip(), "database_unavailable")
                self.assertEqual(list(self.exchanges.iterdir()), [])
        asyncio.run(check())
        self.accept(FakeDatabase(), "--exchange", X, "after release")
# TEST-TIER-END trunks/trivial/tests/test_repeat.py::Repeats.test_another_process_cannot_claim_while_the_root_is_locked_and_its_wait_is_bounded
