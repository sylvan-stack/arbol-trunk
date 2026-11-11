# Compatibility entry: the mid-tier implementation lives in trunks/trivial/tests/mid/archived/trunks/trivial/scripts/check_build.py.
# Keep the original module/package and __file__ so existing fixtures resolve unchanged.
from pathlib import Path as _TierPath
from typing import TYPE_CHECKING as _TYPE_CHECKING

if _TYPE_CHECKING:
    from mid.archived.trunks.trivial.scripts.check_build import driver_bridge as driver_bridge
    from mid.archived.trunks.trivial.scripts.check_build import live as live
    from mid.archived.trunks.trivial.scripts.check_build import program_policy as program_policy
    from mid.archived.trunks.trivial.scripts.check_build import unit as unit
    from mid.archived.trunks.trivial.scripts.check_build import verify as verify
else:
    _tier_source = _TierPath(__file__).resolve().parents[3] / 'trunks/trivial/tests/mid/archived/trunks/trivial/scripts/check_build.py'
    exec(compile(_tier_source.read_bytes(), str(_tier_source), "exec"), globals())
