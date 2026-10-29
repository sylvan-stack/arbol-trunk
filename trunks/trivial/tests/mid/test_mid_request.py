"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_request as _support
from test_request import (
    Any,
    CHAT,
    EXCHANGE,
    HISTORY,
    Path,
    Request,
    json,
    os,
    run_request,
    stat,
    tempfile,
    unittest,
    write_request,
)


class Request(_support.Request):
# TEST-TIER-BEGIN trunks/trivial/tests/test_request.py::Request.test_the_second_message_of_a_chat_is_the_example_of_trv_0
    def test_the_second_message_of_a_chat_is_the_example_of_trv_0(self) -> None:
        request = run_request(exchange=EXCHANGE, chat=CHAT, route={"driver": "claude", "subscription": "anthropic",
                                                                   "model": "sonnet", "effort": "high"},
                              working_folder="/Users/sam/repos/shop", history=HISTORY,
                              message="Add a --clean option to it.")
        self.assertEqual(request, {
            "runId": "2d4f6a8c-1b3e-4c5d-8e7f-9a0b1c2d3e4f.1",
            "subscriptionId": "anthropic",
            "model": "sonnet",
            "effort": "high",
            "workingDirectory": "/Users/sam/repos/shop",
            "history": HISTORY,
            "input": {"role": "user", "text": "Add a --clean option to it."},
            "chatSessionId": "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b",
            "tools": "all",
        })
# TEST-TIER-END trunks/trivial/tests/test_request.py::Request.test_the_second_message_of_a_chat_is_the_example_of_trv_0

# TEST-TIER-BEGIN trunks/trivial/tests/test_request.py::Request.test_the_first_message_has_an_empty_history_and_only_what_the_route_names
    def test_the_first_message_has_an_empty_history_and_only_what_the_route_names(self) -> None:
        request = run_request(exchange=EXCHANGE, chat=CHAT, route={"driver": "claude"}, working_folder="/w",
                              history=[], message="What does build.sh do?")
        self.assertEqual(list(request), ["runId", "workingDirectory", "history", "input", "chatSessionId", "tools"])
        self.assertEqual(request["history"], [])
# TEST-TIER-END trunks/trivial/tests/test_request.py::Request.test_the_first_message_has_an_empty_history_and_only_what_the_route_names

# TEST-TIER-BEGIN trunks/trivial/tests/test_request.py::Request.test_nothing_of_its_own
    def test_nothing_of_its_own(self) -> None:
        request = run_request(exchange=EXCHANGE, chat=CHAT, route={"driver": "claude", "subscription": "zai",
                                                                   "model": "glm"}, working_folder="/w",
                              history=[], message="hi")
        for field in ("systemPrompt", "limits", "labels", "additionalDirectories", "searchPath", "serviceTier",
                      "driver"):
            self.assertNotIn(field, request)
# TEST-TIER-END trunks/trivial/tests/test_request.py::Request.test_nothing_of_its_own

# TEST-TIER-BEGIN trunks/trivial/tests/test_request.py::Request.test_it_is_written_into_the_folder_with_the_mode_0600
    def test_it_is_written_into_the_folder_with_the_mode_0600(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            os.umask(0o022)
            file = write_request(Path(folder), {"runId": "x.1"})
            self.assertEqual(file.name, "run-1.json")
            self.assertEqual(stat.S_IMODE(os.stat(file).st_mode), 0o600)
            self.assertEqual(json.loads(file.read_text()), {"runId": "x.1"})
# TEST-TIER-END trunks/trivial/tests/test_request.py::Request.test_it_is_written_into_the_folder_with_the_mode_0600
