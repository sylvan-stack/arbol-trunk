"""Unit gate for the numbered Steady package."""

import fcntl
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from arbol_trunk_steady.admission import Admission  # noqa: E402
from arbol_trunk_steady.errors import Refusal  # noqa: E402
from arbol_trunk_steady.phase_details import replay_phase_details  # noqa: E402


class WriterAdmission(unittest.TestCase):
    def test_steady_refuses_exclusive_writer_lock_and_old_layout_marker(self) -> None:
        with TemporaryDirectory() as directory:
            runtime = Path(directory)
            admission_folder = runtime / "writer-admission"
            admission_folder.mkdir(mode=0o700)
            for filename in ("gate.lock", "writers.lock", "owner.lock"):
                (admission_folder / filename).touch(mode=0o600)
            marker = admission_folder / "state.json"
            marker.touch(mode=0o600)
            generation = "a" * 32
            state = {
                "format": 2,
                "state": "normal",
                "generation": generation,
                "source": {"host": directory, "port": 5432, "database": "fixture", "databaseOid": 1},
                "session": None,
                "release": "b" * 64,
            }
            marker.write_text(json.dumps(state))
            admission = Admission(runtime)

            with admission.lease("normal", generation=generation) as lease:
                self.assertEqual(lease.state.generation, generation)
            with (admission_folder / "writers.lock").open("r+b") as writers:
                fcntl.flock(writers, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaises(Refusal) as blocked:
                    with admission.lease("normal", generation=generation):
                        self.fail("Steady acquired a writer lease while the exclusive lock was held.")
                self.assertEqual(blocked.exception.code, "maintenance")

            with admission.lease("normal", generation=generation) as lease:
                self.assertEqual(lease.state.generation, generation)
            marker.write_text(json.dumps({**state, "format": 1}))
            with self.assertRaises(Refusal) as incompatible:
                with admission.lease("normal", generation=generation):
                    self.fail("Steady acquired a writer lease with a layout-1 marker.")
            self.assertEqual(incompatible.exception.code, "maintenance")


class PhaseReplay(unittest.TestCase):
    def test_phase_replay_preserves_exact_complete_records_before_a_torn_append(self) -> None:
        start = b'{"n":1, "phase":"execution", "startedAt":"2026-11-19T00:00:00Z"}'
        command = (b'{"n":2,"phase":"execution","command":{"kind":"provider",'
                   b'"parameters":{"text":"\\u00f1\\u0000","exactInteger":9007199254740993}}}')
        torn_tail = b'{"n":3,"phase":"execution","finishedAt":"2026-11-19T00:01:00Z"}'
        exchange = "00000000-0000-0000-0000-000000000001"
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            journal = folder / "phase-details.jsonl"
            journal.touch(mode=0o600)
            journal.write_bytes(b"\n".join((start, command, torn_tail)))

            rows = replay_phase_details(folder, exchange)
            self.assertEqual([(row.exchange, row.position, row.entry.encode("ascii")) for row in rows],
                             [(exchange, 1, start), (exchange, 2, command)])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent))
    if not suite.countTestCases():
        raise SystemExit("The packaged Steady unit gate found no top-tier tests.")
    raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
