import json
import os
import tempfile
import unittest
from pathlib import Path

from arbol_trunk_trivial.end import End, end_of_run, write_end
from arbol_trunk_trivial.events import EventsFile
from arbol_trunk_trivial.folder import ExchangeFolder

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
RATE = {"code": "rate_limited", "message": "…", "retryable": True, "retryAfterSeconds": 1800}


class Ends(unittest.TestCase):
    def test_the_state_is_the_runs_outcome(self) -> None:
        self.assertEqual((end_of_run({"outcome": "completed"}).state, end_of_run({"outcome": "completed"}).error),
                         ("completed", None))
        self.assertEqual(end_of_run({"outcome": "cancelled"}).exit_status, 2)
        failed = end_of_run({"outcome": "failed", "error": RATE})
        self.assertEqual((failed.state, failed.error, failed.exit_status), ("failed", RATE, 1))

    def test_without_a_finished_event_the_exchange_fails_with_driver_failed(self) -> None:
        end = end_of_run(None)
        self.assertEqual(end.state, "failed")
        assert end.error is not None
        self.assertEqual(end.error["code"], "driver_failed")

    def test_the_end_is_the_last_line_and_the_same_end_is_in_the_record(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            folder = ExchangeFolder.make(Path(name), X, {"exchange": X, "signsOfLife": {}})
            events = EventsFile(folder.path / "events.jsonl")
            self.addCleanup(events.close)
            end = end_of_run({"outcome": "failed", "error": RATE})
            write_end(events, folder, end)
            lines = (folder.path / "events.jsonl").read_text().splitlines()
            self.assertEqual(json.loads(lines[-1]), {"n": 1, "end": end.value()})
            self.assertEqual(json.loads((folder.path / "record.json").read_text())["end"], end.value())
            self.assertEqual(set(end.value()), {"state", "at", "error"})
            self.assertNotIn("error", End("completed", end.at).value())
            self.assertEqual(sorted(os.listdir(folder.path)), ["control", "events.jsonl", "record.json"])


if __name__ == "__main__":
    unittest.main()
