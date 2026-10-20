"""Stand-ins for programs outside the Trunk, written as small scripts into a test's own folder."""

from __future__ import annotations

import os
from pathlib import Path

CAPABILITIES = """
case "$*" in
  info) printf '%s\\n' '{"driver":"claude","contract":2}'; exit 0 ;;
  "subscriptions families") printf '%s\\n' '[{"id":"anthropic"}]'; exit 0 ;;
  "subscriptions list") printf '%s\\n' '[{"id":"anthropic","family":"anthropic"}]'; exit 0 ;;
esac
"""


def with_capabilities(script: str) -> str:
    return script.replace("#!/bin/sh\n", "#!/bin/sh\n" + CAPABILITIES, 1)


def security_stand_in(folder: Path, *, status: int = 0, password: str = "secret", sleep: float = 0) -> Path:
    """A `security` that records its arguments, waits `sleep` seconds and ends with `status`, printing `password`."""
    script = folder / "security"
    script.write_text(
        "#!/bin/sh\n"
        f'printf "%s\\n" "$*" >> "{folder}/security.args"\n'
        f"sleep {sleep}\n"
        f'[ {status} -eq 0 ] && printf "%s\\n" "{password}"\n'
        f"exit {status}\n", encoding="utf-8")
    os.chmod(script, 0o755)
    return script
