# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import asyncio
import shlex
import sys
import tempfile
import unittest
from pathlib import Path

from arbol_trunk_trivial.driver import (
    capabilities,
)


class Capabilities(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.program = self.home / "driver"

    def script(self, source: str) -> str:
        script = self.program.with_suffix(".py")
        script.write_text(source)
        self.program.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} -I -B "
                                f"{shlex.quote(str(script))} \"$@\"\n")
        self.program.chmod(0o755)
        return str(self.program)

    def check(self, driver: str = "pi", subscription: str | None = "test-zai") -> None:
        asyncio.run(capabilities(str(self.program), driver, subscription, str(self.home), self.home, lambda: False))

    def fixture(self, *, contract: object = 2, family: str = "zai", offered: str = "zai") -> None:
        self.script("import json,sys\n"
                    f"replies = {repr({'info': {'driver': 'pi', 'contract': contract}, 'subscriptions families':
                                     [{'id': offered}], 'subscriptions list':
                                     [{'id': 'test-zai', 'family': family}]})}\n"
                    "print(json.dumps(replies[' '.join(sys.argv[1:])]))\n")


# Archived complete imports; restore needed names in their original scope, not at this file tail.
