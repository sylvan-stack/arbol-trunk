# Arbol Trunk

This repository holds Arbol 2's Trunks, each in its own `trunks/<code name>/` folder. The [Trivial Trunk](trunks/trivial/README.md) is the default: one Driver run for each Chat Exchange, using the route it is handed. It implements Root Contract 1 and runs independently of the Root manager.

| | |
|---|---|
| Package | `@sylvan-stack/arbol-trunk` 1.0.0 |
| Artifact corpus | `~/Artifacts/arbol-trunk` (GitHub `sylvan-stack/arbol-trunk-artifacts`) |

## Build and check the Trivial Trunk

From a clean login shell, after changes have been merged and the readonly checkout updated:

```sh
arbol-builds build arbol-trunk/trivial
arbol-trunk list
```

The Build Tool reads `trunks/trivial/arbol-build.json` from `~/repos/sylvan-stack/readonly/arbol-trunk`. Each package carries checksum-pinned CPython 3.14.8, locked binary psycopg, its source and tests, and a file manifest. Its entry runs its own isolated interpreter; it needs no development environment or separately installed PostgreSQL client library.

The Build must pass `unit` (the top-tier packaged tests, integrity, imports and metadata) and `live` (one real message through the installed Claude Driver on `test-anthropic` / `haiku`). The complete Root Contract suite is mid tier: since SYL-329 the Build does not run it, and it runs when the owner asks. The live check makes and removes its own temporary home, PostgreSQL server and Root record. PostgreSQL 17's programs must be on the search path. The live check uses the Driver's test state, `~/Library/Application Support/Arbol/drivers/arbol-claude-driver`; an absolute `ARBOL_BUILD_TEST_STATE_DIR` overrides it. Each real qualification consumes tokens, printed in the Build log. A failed check leaves the last working Build selected.

See the [Trivial Trunk README](trunks/trivial/README.md) for development and offline checks. The [specification](https://github.com/sylvan-stack/arbol-trunk-artifacts/blob/main/trunks/trivial/specs/00-the-trivial-trunk.md) defines the behavior and Build checks.

## Sylvan Stack 2

| Repository | Package | Version | Artifact corpus | Artifact repository |
|---|---|---|---|---|
| `arbol` | `@sylvan-stack/arbol` | 2.0.0 | `~/Artifacts/arbol` | `sylvan-stack/arbol-artifacts` |
| `arbol-root` | `@sylvan-stack/arbol-root` | 1.0.0 | `~/Artifacts/arbol-root` | `sylvan-stack/arbol-root-artifacts` |
| `arbol-trunk` | `@sylvan-stack/arbol-trunk` | 1.0.0 | `~/Artifacts/arbol-trunk` | `sylvan-stack/arbol-trunk-artifacts` |
| `arbol-claude-driver` | `@sylvan-stack/arbol-claude-driver` | 1.0.0 | `~/Artifacts/arbol-claude-driver` | `sylvan-stack/arbol-claude-driver-artifacts` |
| `arbol-codex-driver` | `@sylvan-stack/arbol-codex-driver` | 1.0.0 | `~/Artifacts/arbol-codex-driver` | `sylvan-stack/arbol-codex-driver-artifacts` |
| `arbol-browser` | `@sylvan-stack/arbol-browser` | 1.0.0 | `~/Artifacts/arbol-browser` | `sylvan-stack/arbol-browser-artifacts` |
| `mycel` | `@sylvan-stack/mycel` | 2.0.0 | `~/Artifacts/mycel` | `sylvan-stack/mycel-artifacts` |
| `arbol-pi-driver` | `@sylvan-stack/arbol-pi-driver` | 1.0.0 | `~/Artifacts/arbol-pi-driver` | `sylvan-stack/arbol-pi-driver-artifacts` |
| `workspace-ledger` | `workspace-ledger` (planned) | 1.0.0 | `~/Artifacts/sylvan-stack/repos/workspace-ledger` | `sylvan-stack/workspace-ledger-artifacts` |
