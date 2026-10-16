"""The command of a Build of the Trivial Trunk, as the launcher `arbol-trunk` starts it (RCT-0):

    arbol-trunk-trivial --root <root> run [--request <file>] [--exchange <id>] [--chat <id>] [--cwd <folder>]
                                          [--driver <d>] [--subscription <s>] [--model <m>] [--effort <e>]
                                          [--detach] ["<message>"]

It answers with one line on standard output, the acceptance line or a refusal, and runs the Exchange to its end.
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

from .build import BuildRecordError, build_number
from .command import handed, parse
from .database import conninfo, postgres
from .detach import lead_process_group
from .errors import Refusal
from .process import started_at
from .run import run_exchange
from .start import prepare


def main(args: list[str]) -> int:
    started = time.monotonic()
    lead_process_group()
    try:
        build = build_number()
        prepared = prepare(handed(parse(args)), Path.home())
    except BuildRecordError as error:
        print(Refusal("trunk_failed", str(error)).line(), flush=True)
        return 1
    except Refusal as refusal:
        print(refusal.line(), flush=True)
        return 1
    connect = postgres(conninfo(prepared.address, prepared.root.database, prepared.password))
    process = {"pid": os.getpid(), "startedAt": started_at()}
    return asyncio.run(run_exchange(prepared, connect, build=build, process=process, started=started))


def entry() -> None:
    sys.exit(main(sys.argv[1:]))
