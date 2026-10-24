# The Trivial Trunk

The default Trunk of every Arbol Root: for each Chat Exchange it makes exactly one inference run of a Driver with the route it is handed. Its specification is [TRV-0](https://github.com/sylvan-stack/arbol-trunk-artifacts/blob/main/trunks/trivial/specs/00-the-trivial-trunk.md); it implements version 1 of the [Root Contract](https://github.com/sylvan-stack/arbol-root-artifacts/blob/main/contract/README.md).

Before inference it checks `info`, offered families and Subscriptions, accepting Driver Contracts 1 and 2. Unknown or retired selections fail without fallback; model and effort choices pass unchanged to the Driver. Each metadata query is bounded and cancellable. An unfinished `~/.arbol/pi-cutover.json` migration blocks its affected routes until verified completion or explicit restore. Caller history remains the source for a first Pi run.

Typed Python 3.14 with the standard library and psycopg 3 only. From this folder:

```sh
uv sync --group dev
PYTHONPATH=src uv run --no-sync python -B -m unittest discover -s tests
uv run --no-sync ruff check src tests bin/entry.py
uv run --no-sync mypy
```

Until its first Build, it runs from this checkout through `bin/arbol-trunk-trivial`, which starts `bin/entry.py` with the folder's own Python and reports the build number `0`. The Root Contract's conformance suite checks it so:

```sh
python3.14 ~/repos/sylvan-stack/arbol-root/contract/conformance/bin/rct-conformance.py \
  --trunk ~/repos/sylvan-stack/arbol-trunk/trunks/trivial/bin/arbol-trunk-trivial --root-contract 1 --only R1
```

Without `--detach`, `run` prints the acceptance and then the saved event lines, and returns 0 for completed, 1 for failed and 2 for cancelled. An unread or closed output pipe does not stop the Exchange. SIGTERM, Ctrl-C and a foreground terminal hang-up end its process group without recording an Exchange end; `bin/arbol-trunk-trivial --root <root> settle <exchange>` then recovers its saved text, tool calls and usage as interrupted. A recorded end keeps its state. The `R2` and `R10` conformance scenarios check these paths.
