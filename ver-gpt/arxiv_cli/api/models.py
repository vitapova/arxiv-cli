from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional


@dataclass(frozen=True)
class Paper:
    """Domain model for an arXiv paper."""

    arxiv_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    published: Optional[datetime]
    updated: Optional[datetime]
    links: dict[str, str]

    @property
    def pdf_url(self) -> Optional[str]:
        return self.links.get("pdf")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["published"] = self.published.isoformat() if self.published else None
        d["updated"] = self.updated.isoformat() if self.updated else None
        return d
