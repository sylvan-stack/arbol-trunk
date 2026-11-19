"""Replace only characters PostgreSQL cannot store, at the SQL boundary (RCT-3.10)."""

from __future__ import annotations

from typing import Any

from psycopg.types.json import Jsonb


def stored(value: Any) -> Any:
    """Keep events and in-memory values intact; sanitize every SQL string, including JSON keys and values."""
    if isinstance(value, str):
        return value.replace("\0", "\ufffd").encode("utf-16-le", "surrogatepass").decode("utf-16-le", "replace")
    if isinstance(value, Jsonb):
        return Jsonb(stored(value.obj))
    if isinstance(value, dict):
        return {stored(key): stored(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stored(item) for item in value]
    if isinstance(value, tuple):
        return tuple(stored(item) for item in value)
    return value
