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
