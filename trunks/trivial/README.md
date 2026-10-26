# The Trivial Trunk

The default Trunk of every Arbol Root: for each Chat Exchange it makes exactly one inference run of a Driver with the route it is handed. Its specification is [TRV-0](https://github.com/sylvan-stack/arbol-trunk-artifacts/blob/main/trunks/trivial/specs/00-the-trivial-trunk.md); it implements version 1 of the [Root Contract](https://github.com/sylvan-stack/arbol-root-artifacts/blob/main/contract/README.md).

Before inference it checks `info`, offered families and Subscriptions, accepting Driver Contracts 1 and 2. Unknown or retired selections fail without fallback; model and effort choices pass unchanged to the Driver. Each metadata query is bounded and cancellable. An unfinished `~/.arbol/pi-cutover.json` migration blocks its affected routes until verified completion or explicit restore. Caller history remains the source for a first Pi run.

Typed Python 3.14 with the standard library and psycopg 3 only. From this folder:

```sh
uv sync --locked --group dev
PYTHONPATH=src uv run --no-sync python -B -m unittest discover -s tests
uv run --no-sync ruff check src tests scripts bin/entry.py
uv run --no-sync mypy
```

From a checkout, `bin/arbol-trunk-trivial` starts `bin/entry.py` with the folder's own `.venv` Python and reports Build `0`. A package uses only its own `runtime/python/bin/python3.14`, with `-I -B`; a marked package with a missing runtime fails. A numbered package reads its number from its own `build.json`. The complete Root Contract suite checks the checkout so:

```sh
python3.14 ~/repos/sylvan-stack/readonly/arbol-root/contract/conformance/bin/rct-conformance.py \
  --trunk "$PWD/bin/arbol-trunk-trivial" --root-contract 1
```

To rehearse packaging without installing or sending a message, create an empty temporary directory outside this checkout, then run:

```sh
uv run --no-sync python -B scripts/package_build.py --candidate /absolute/temporary/package
/absolute/temporary/package/runtime/python/bin/python3.14 -I -B \
  /absolute/temporary/package/scripts/check_build.py unit --candidate /absolute/temporary/package
```

The package includes its own pinned interpreter, binary psycopg, tests and manifest. The unit check rejects changed files, unsupported imports, another Trunk's source, or a mismatch between the program and `rootContracts`. The conformance suite can use the temporary package's `bin/arbol-trunk-trivial` as `--trunk` too. Candidates remain Build `0` and never enter the installed registry. Remove the temporary directory after checking it.

The installed Build is made with `arbol-builds build arbol-trunk/trivial`, from merged readonly source, as the [repository README](../../README.md) describes. Its `live` check sends one real message on the Claude Driver's test Subscription and prints its usage; it is separate from these offline development checks.

Without `--detach`, `run` prints the acceptance and then the saved event lines, and returns 0 for completed, 1 for failed and 2 for cancelled. An unread or closed output pipe does not stop the Exchange. SIGTERM, Ctrl-C and a foreground terminal hang-up end its process group without recording an Exchange end; `bin/arbol-trunk-trivial --root <root> settle <exchange>` then recovers its saved text, tool calls and usage as interrupted. A recorded end keeps its state. The `R2` and `R10` conformance scenarios check these paths.
