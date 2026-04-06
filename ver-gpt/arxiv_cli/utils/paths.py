from __future__ import annotations

import re


_invalid = re.compile(r"[^A-Za-z0-9._-]+")


def safe_filename(s: str) -> str:
    """Make a conservative filename component (ASCII-ish)."""
    s = s.strip().replace(" ", "_")
    s = _invalid.sub("_", s)
    s = s.strip("._-")
    return s or "unknown"
