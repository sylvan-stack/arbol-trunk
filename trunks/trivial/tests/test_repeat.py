# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
import os

from test_accept import AcceptanceHome

from arbol_trunk_trivial.folder import ExchangeFolder
from arbol_trunk_trivial.process import started_at

X = "7f3a2c1e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"


class Repeats(AcceptanceHome):


    def abandoned(self, *, live: bool = False, dot: bool = False) -> ExchangeFolder:
        folder = ExchangeFolder.make(self.exchanges, X, {
            "exchange": X, "process": {"pid": os.getpid(),
                                       "startedAt": started_at() if live else "2000-01-01T00:00:00Z"}})
        if dot:
            folder.path.rename(self.exchanges / f".{X}.new")
        return folder


# Archived complete imports; restore needed names in their original scope, not at this file tail.
