"""Exercise the actual wait paths named by RCT-4, with a scale of ten and moved awake clocks."""

import asyncio
import signal
from unittest import mock

from fake_driver import MovedClock, ScriptedDriver, finished
from fakes import FakeDatabase
from test_life import LifeHome

from arbol_trunk_trivial.end import End, save_end
from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.life import SignsOfLife
from arbol_trunk_trivial.rows import MessageRow, RowMaker
from arbol_trunk_trivial.run import drive
from arbol_trunk_trivial.saver import Saver
from arbol_trunk_trivial.termination import end_group
from arbol_trunk_trivial.watch import Watch


class TimeScaledWaits(LifeHome):
    def test_each_existing_contract_wait_uses_the_divided_duration(self) -> None:
        observed: dict[str, float] = {}

        async def exercise() -> None:
            driver = ScriptedDriver(self.clock, holds_output=True)
            driver.at(0, 'event', finished(1))
            saver = Saver(FakeDatabase().connect())
            events = EventsFile(self.folder.path / 'events.jsonl')
            try:
                await drive(driver, events, RowMaker('x'), saver, clock=self.clock, life=self.life)
            finally:
                events.close()
            assert driver.killed_at is not None
            observed['driver round'] = max(driver.waits)
            observed['Driver stop after finished'] = driver.killed_at
            observed['output after process exit'] = self.clock.since_start() - driver.killed_at

            silent_clock = MovedClock()
            silent = ScriptedDriver(silent_clock)
            silent_events = EventsFile(self.folder.path / 'events.jsonl')
            try:
                await drive(silent, silent_events, RowMaker('x'), Saver(FakeDatabase().connect()), clock=silent_clock)
            finally:
                silent_events.close()
            observed['Driver silence'] = silent.control[0][0]

            original_wait = asyncio.wait
            async def immediate() -> int:
                return 42
            with mock.patch('arbol_trunk_trivial.life.asyncio.wait', wraps=original_wait) as poll:
                self.assertEqual(await self.life.wait(immediate(), 'database'), 42)
            observed['startup/save work poll'] = poll.call_args.kwargs['timeout']

            keeper = Saver(FakeDatabase(fail_connect=1).connect())
            keeper.add([MessageRow('x', 1, 'text')])
            async def retry(seconds: float) -> None:
                observed['saving retry'] = seconds
                raise StopAsyncIteration
            with (mock.patch('arbol_trunk_trivial.saver.asyncio.sleep', side_effect=retry),
                  self.assertRaises(StopAsyncIteration)):
                await keeper._run()

            clock = MovedClock()
            async def advance(seconds: float) -> None:
                observed['end retry'] = seconds
                clock.t += seconds
            from datetime import UTC, datetime
            with (mock.patch('arbol_trunk_trivial.end.uptime', side_effect=clock.now),
                  mock.patch('arbol_trunk_trivial.end.asyncio.sleep', side_effect=advance)):
                saved = await save_end(Saver(FakeDatabase(fail_connect=100).connect()), 'x', [],
                                       End('completed', datetime(2026, 10, 26, tzinfo=UTC)))
            self.assertFalse(saved)
            observed['end tries'] = clock.since_start()

        with mock.patch.dict('os.environ', {'ARBOL_TEST_TIME_SCALE': '10'}):
            asyncio.run(exercise())
            clock = MovedClock()
            life = SignsOfLife(clock=clock)
            end = mock.Mock()
            watch = Watch(life, end)
            clock.t += 5.9
            self.assertFalse(watch.look())
            clock.t += 0.1
            self.assertTrue(watch.look())
            observed['watch age'] = clock.since_start()
            idle = Watch(SignsOfLife(clock=clock), end)
            idle.done = mock.Mock()
            idle.done.wait.side_effect = [False, True]
            idle._run()
            observed['watch look'] = idle.done.wait.call_args.args[0]

            with (mock.patch('arbol_trunk_trivial.termination.uptime', side_effect=[0.0, 0.0, 0.5]),
                  mock.patch('arbol_trunk_trivial.termination.time.sleep') as sleep,
                  mock.patch('arbol_trunk_trivial.termination.os.getpgrp', return_value=123),
                  mock.patch('arbol_trunk_trivial.termination.os.killpg') as kill,
                  mock.patch('arbol_trunk_trivial.termination.signal.signal'),
                  mock.patch('arbol_trunk_trivial.termination.os._exit', side_effect=SystemExit),
                  self.assertRaises(SystemExit)):
                end_group()
            observed['group grace'] = sleep.call_args.args[0]
            self.assertEqual(kill.call_args_list, [mock.call(123, signal.SIGTERM), mock.call(123, signal.SIGKILL)])

        expected = {'driver round': 0.1, 'Driver stop after finished': 1.6, 'output after process exit': 0.1,
                    'startup/save work poll': 0.1, 'saving retry': 0.5, 'end retry': 0.5, 'end tries': 6.0,
                    'watch age': 6.0, 'watch look': 0.1, 'group grace': 0.5, 'Driver silence': 96.0}
        self.assertEqual(set(observed), set(expected))
        for name, value in expected.items():
            with self.subTest(wait=name):
                self.assertAlmostEqual(observed[name], value)
