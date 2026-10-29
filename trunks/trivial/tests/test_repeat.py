# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
import asyncio
import copy
import json
import subprocess
import sys
import time
from pathlib import Path
from unittest import mock

from fakes import FakeConnection, FakeDatabase
from test_accept import CHAT, AcceptanceHome
from arbol_trunk_trivial.accept import Exchange, Repeated, accept_message
from arbol_trunk_trivial.claim import root_lock
from arbol_trunk_trivial.database import Acceptance, Accepted, DuplicateExchange, PriorExchange
from arbol_trunk_trivial.errors import Refusal
from arbol_trunk_trivial.output import Output
from arbol_trunk_trivial.run import run_exchange

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
