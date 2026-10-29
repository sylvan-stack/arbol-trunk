"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_detach as _support
from test_detach import (
    Background,
    CHILD,
    Path,
    SOURCE,
    json,
    os,
    select,
    subprocess,
    sys,
    tempfile,
    time,
    unittest,
)


class Background(_support.Background):
# TEST-TIER-BEGIN trunks/trivial/tests/test_detach.py::Background.test_after_the_line_its_output_goes_nowhere_and_sighup_is_ignored
    def test_after_the_line_its_output_goes_nowhere_and_sighup_is_ignored(self) -> None:
        line, report, child = self.run_child(new_session=True)
        self.assertEqual(line, '{"accepted":true}\n')
        self.assertEqual(child.returncode, 0)  # it lived on through SIGHUP and the closed pipe
        self.assertEqual(report["pgid"], report["pid"])
        self.assertEqual(report["null"], [True, True, True])
# TEST-TIER-END trunks/trivial/tests/test_detach.py::Background.test_after_the_line_its_output_goes_nowhere_and_sighup_is_ignored

# TEST-TIER-BEGIN trunks/trivial/tests/test_detach.py::Background.test_a_trunk_that_does_not_lead_its_group_makes_itself_the_leader_of_a_new_one
    def test_a_trunk_that_does_not_lead_its_group_makes_itself_the_leader_of_a_new_one(self) -> None:
        _line, report, child = self.run_child(new_session=False)
        self.assertEqual(child.returncode, 0)
        self.assertEqual(report["pgid"], report["pid"])
        self.assertNotEqual(report["pgid"], os.getpgrp())
# TEST-TIER-END trunks/trivial/tests/test_detach.py::Background.test_a_trunk_that_does_not_lead_its_group_makes_itself_the_leader_of_a_new_one
