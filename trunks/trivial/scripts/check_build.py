# Compatibility entry: the mid-tier implementation lives in trunks/trivial/tests/mid/archived/trunks/trivial/scripts/check_build.py.
# Keep the original module/package and __file__ so existing fixtures resolve unchanged.
from pathlib import Path as _TierPath
_tier_source = _TierPath(__file__).resolve().parents[3] / 'trunks/trivial/tests/mid/archived/trunks/trivial/scripts/check_build.py'
exec(compile(_tier_source.read_bytes(), str(_tier_source), "exec"), globals())
