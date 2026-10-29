"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_output as _support
from test_output import (Output ,mock ,os ,signal)


class ForegroundOutput(_support.ForegroundOutput):


# TEST-TIER-BEGIN trunks/trivial/tests/test_output.py::ForegroundOutput.test_a_termination_signal_is_delivered_only_after_shared_descriptor_flags_are_restored
    def test_a_termination_signal_is_delivered_only_after_shared_descriptor_flags_are_restored(self) -> None:
        reader, writer = os.pipe()
        self.addCleanup(os.close, reader)
        self.addCleanup(os.close, writer)
        seen: list[bool] = []
        old_handler = signal.signal(signal.SIGTERM, lambda *_args: seen.append(os.get_blocking(writer)))
        self.addCleanup(signal.signal, signal.SIGTERM, old_handler)
        write = os.write

        def interrupted(descriptor: int, data: bytes) -> int:
            os.kill(os.getpid(), signal.SIGTERM)
            return write(descriptor, data)

        with mock.patch("arbol_trunk_trivial.output.os.write", side_effect=interrupted):
            Output(descriptor=writer).line("hello")
        self.assertEqual(seen, [True])
        self.assertEqual(os.read(reader, 6), b"hello\n")
# TEST-TIER-END trunks/trivial/tests/test_output.py::ForegroundOutput.test_a_termination_signal_is_delivered_only_after_shared_descriptor_flags_are_restored
