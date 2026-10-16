"""The command of a Build of the Trivial Trunk, as the launcher `arbol-trunk` starts it (RCT-0):

    arbol-trunk-trivial --root <root> run [<options>] ["<message>"]
"""

from __future__ import annotations

import sys


def main(args: list[str]) -> int:
    print('{"error":{"code":"invalid_input","message":"Not built yet."}}', flush=True)
    return 1


def entry() -> None:
    sys.exit(main(sys.argv[1:]))
