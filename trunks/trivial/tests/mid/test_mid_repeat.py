"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_repeat as _support
from test_repeat import (FakeDatabase ,Path ,X ,asyncio ,root_lock ,subprocess ,sys ,time)


class Repeats(_support.Repeats):


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
