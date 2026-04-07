from __future__ import annotations

import re


_ARXIV_ID_RE = re.compile(
    r"^(?P<id>(?:\d{4}\.\d{4,5})(?:v\d+)?|[a-z-]+/\d{7}(?:v\d+)?)$",
    re.IGNORECASE,
)


def normalize_arxiv_id(s: str) -> str:
    """Extract/normalize an arXiv id from input.

    Accepts plain ids (e.g. 2402.05964v2) and URLs like:
    - https://arxiv.org/abs/2402.05964v2
    - https://arxiv.org/pdf/2402.05964v2.pdf

    Note: the returned id may include a version suffix (vN).
    """
    s = s.strip()
    s = s.removeprefix("https://").removeprefix("http://")
    s = s.replace("arxiv.org/abs/", "").replace("arxiv.org/pdf/", "")
    if s.endswith(".pdf"):
        s = s[: -len(".pdf")]
    s = s.strip("/")

    m = _ARXIV_ID_RE.match(s)
    if not m:
        raise ValueError(f"Invalid arXiv id: {s}")
    return m.group("id")


def base_arxiv_id(arxiv_id: str) -> str:
    """Strip version suffix from arXiv id (e.g. 2402.05964v2 -> 2402.05964)."""
    if "v" in arxiv_id:
        left, right = arxiv_id.rsplit("v", 1)
        if right.isdigit():
            return left
    return arxiv_id


def parse_version(arxiv_id: str) -> int | None:
    """Extract integer version from arXiv id, if present."""
    if "v" not in arxiv_id:
        return None
    left, right = arxiv_id.rsplit("v", 1)
    if not right.isdigit() or not left:
        return None
    return int(right)
