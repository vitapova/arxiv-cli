from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional


Status = Literal["unread", "read", "starred"]


@dataclass
class ArticleRecord:
    """Canonical stored representation of a paper in the local library."""

    arxiv_id: str
    title: str = ""
    summary: str = ""
    authors: list[str] = None  # type: ignore[assignment]
    categories: list[str] = None  # type: ignore[assignment]

    published: Optional[str] = None  # ISO datetime
    updated: Optional[str] = None  # ISO datetime

    added_at: Optional[str] = None  # ISO datetime
    status: Status = "unread"
    tags: list[str] = None  # type: ignore[assignment]

    links: dict[str, str] = None  # type: ignore[assignment]
    version: Optional[int] = None

    def __post_init__(self) -> None:
        if self.authors is None:
            self.authors = []
        if self.categories is None:
            self.categories = []
        if self.tags is None:
            self.tags = []
        if self.links is None:
            self.links = {}


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
