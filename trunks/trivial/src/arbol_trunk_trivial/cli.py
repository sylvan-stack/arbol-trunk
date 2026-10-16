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
from collections.abc import Callable
from pathlib import Path

from .build import BuildRecordError, build_number
from .command import handed, parse
from .database import Connect, conninfo, postgres
from .detach import lead_process_group
from .errors import Refusal
from .process import started_at
from .root import SECURITY
from .run import Output, run_exchange
from .start import Prepared, prepare

Connector = Callable[[Prepared], Connect]


def postgres_for(prepared: Prepared) -> Connect:
    """The Root's own database, at the address of `~/.arbol/database.json` with the password of the Keychain."""
    return postgres(conninfo(prepared.address, prepared.root.database, prepared.password))


async def start(args: list[str], *, home: Path, started: float, connector: Connector = postgres_for,
                security: str = SECURITY, started_in: str | None = None, output: Output | None = None,
                search_path: str | None = None) -> int:
    """`run` from its command line to its end: one answer on standard output, the acceptance line or a refusal, then
    the Exchange. `started` is the start of the Trunk (time.monotonic()); a refusal is the exit status 1 (RCT-2)."""
    output = output or Output()
    try:
        build = build_number()
        prepared = prepare(handed(parse(args), started_in), home, security)
    except BuildRecordError as error:
        output.line(Refusal("trunk_failed", str(error)).line())
        return 1
    except Refusal as refusal:
        output.line(refusal.line())
        return 1
    process = {"pid": os.getpid(), "startedAt": started_at()}
    return await run_exchange(prepared, connector(prepared), build=build, process=process, started=started,
                              output=output, search_path=search_path)


def main(args: list[str]) -> int:
    started = time.monotonic()
    lead_process_group()
    return asyncio.run(start(args, home=Path.home(), started=started))


def entry() -> None:
    sys.exit(main(sys.argv[1:]))
