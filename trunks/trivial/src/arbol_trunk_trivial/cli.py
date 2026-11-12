"""The command of a Build of the Trivial Trunk, as the launcher `arbol-trunk` starts it (RCT-0):

    arbol-trunk-trivial run [--request <file>] [--exchange <id>] [--chat <id>] [--cwd <folder>]
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

from .accept import ACCEPTANCE_SECONDS, Repeated, find_prior
from .admission import GENERATION_ENV, Admission
from .build import BuildRecordError, build_info
from .command import UUID, handed, parse
from .database import Connect, installed_postgres, preflight
from .detach import lead_process_group
from .errors import Refusal
from .process import started_at
from .root import SECURITY, installation, private_directory
from .run import Output, run_exchange
from .settle import settle_exchange
from .start import Prepared, prepare
from .termination import install_handlers

Connector = Callable[[Prepared], Connect]


async def start(args: list[str], *, home: Path, started: float, connector: Connector | None = None,
                security: str = SECURITY, started_in: str | None = None, output: Output | None = None,
                search_path: str | None = None, settle_connect: Connect | None = None) -> int:
    """`run` from its command line to its end: one answer on standard output, the acceptance line or a refusal, then
    the Exchange. `started` is the start of the Trunk (time.monotonic()); a refusal is the exit status 1 (RCT-2)."""
    output = output or Output()
    try:
        command = parse(args)
        build, compatibility = build_info()
        context = installation(home)
        if command.operation == "settle":
            return await settle_exchange(context, command.options["--exchange"], output=output,
                                         security=security, connect=settle_connect, build=build,
                                         compatibility=compatibility)
        with Admission(context.runtime).lease("normal", generation=os.environ.get(GENERATION_ENV)) as lease:
            if connector is None:
                connect = installed_postgres(context, security, compatibility, lease=lease)
                deadline = started + ACCEPTANCE_SECONDS
                await preflight(connect, deadline)
                exchange = command.options.get("--exchange")
                if exchange is not None and UUID.fullmatch(exchange):
                    prior = await find_prior(connect, exchange, deadline)
                    if prior is not None:
                        raise Repeated(prior)
            prepared = prepare(handed(command, started_in), context)
            if connector is not None:
                connect = connector(prepared)
            private_directory(context.runtime)
            private_directory(context.exchanges)
            process = {"pid": os.getpid(), "startedAt": started_at()}
            return await run_exchange(prepared, connect, build=build, process=process, started=started,
                                      output=output, search_path=search_path)
    except Repeated as repeated:
        output.line(repeated.line)
        return 0
    except BuildRecordError as error:
        output.line(Refusal("trunk_failed", str(error)).line())
        return 1
    except Refusal as refusal:
        output.line(refusal.line())
        return 1



def main(args: list[str]) -> int:
    started = time.monotonic()
    lead_process_group()
    install_handlers()
    return asyncio.run(start(args, home=Path.home(), started=started))


def entry() -> None:
    sys.exit(main(sys.argv[1:]))
