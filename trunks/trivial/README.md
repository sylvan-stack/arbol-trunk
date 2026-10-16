# The Trivial Trunk

The default Trunk of every Arbol Root: for each Chat Exchange it makes exactly one run of a Driver with the route it is handed, and nothing else. Its specification is [TRV-0](https://github.com/sylvan-stack/arbol-trunk-artifacts/blob/main/trunks/trivial/specs/00-the-trivial-trunk.md); it implements version 1 of the [Root Contract](https://github.com/sylvan-stack/arbol-root-artifacts/blob/main/contract/README.md).

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
