import threading
import unittest
from unittest import mock

from fake_driver import MovedClock

from arbol_trunk_trivial.life import SignsOfLife
from arbol_trunk_trivial.watch import Watch


class Watching(unittest.TestCase):
    def test_only_sixty_awake_seconds_without_a_raise_trigger_the_end(self) -> None:
        clock = MovedClock()
        life = SignsOfLife(clock=clock)
        ended: list[float] = []
        watch = Watch(life, lambda: ended.append(clock.now()))
        clock.t += 59
        self.assertFalse(watch.look())
        self.assertEqual(ended, [])
        life.beat()
        clock.t += 59
        self.assertFalse(watch.look())
        clock.t += 1
        self.assertTrue(watch.look())
        self.assertEqual(ended, [clock.t])
        self.assertEqual(life.heartbeat, 1)

    def test_a_wall_clock_jump_does_not_count_as_awake_time(self) -> None:
        clock = MovedClock()
        life = SignsOfLife(clock=clock)
        ended = mock.Mock()
        watch = Watch(life, ended)
        with mock.patch('time.time', return_value=10**12):
            self.assertFalse(watch.look())
        ended.assert_not_called()

    def test_the_second_thread_observes_the_clock_but_never_raises_the_heartbeat(self) -> None:
        clock = MovedClock()
        life = SignsOfLife(clock=clock)
        ended = threading.Event()
        watch = Watch(life, ended.set)
        clock.t += 60
        with mock.patch('arbol_trunk_trivial.watch.LOOK_SECONDS', 0.001):
            watch.start()
            try:
                self.assertTrue(ended.wait(1))
                self.assertEqual(life.heartbeat, 0)
                self.assertEqual(life.last_raised, clock.start)
            finally:
                watch.close()
        self.assertIsNone(watch.thread)

    def test_closing_a_watch_does_not_wait_for_another_look(self) -> None:
        life = SignsOfLife(clock=MovedClock())
        ended = mock.Mock()
        watch = Watch(life, ended)
        watch.start()
        watch.close()
        ended.assert_not_called()
        self.assertIsNone(watch.thread)


class EndingTheGroup(unittest.TestCase):
    def test_the_watch_uses_shared_group_termination_without_raising_or_writing(self) -> None:
        clock = MovedClock()
        life = SignsOfLife(clock=clock)
        clock.t += 60
        with mock.patch('arbol_trunk_trivial.watch.end_group') as end:
            watch = Watch(life)
            self.assertTrue(watch.look())
        end.assert_called_once_with()
        self.assertEqual(life.heartbeat, 0)
        self.assertEqual(life.last_raised, clock.start)
