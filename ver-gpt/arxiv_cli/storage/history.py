from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class VersionEvent:
    arxiv_base_id: str
    seen_version: int
    seen_at: str  # ISO datetime
    updated: Optional[str] = None  # ISO datetime from arXiv metadata

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "VersionEvent":
        return cls(
            arxiv_base_id=d["arxiv_base_id"],
            seen_version=int(d["seen_version"]),
            seen_at=d["seen_at"],
            updated=d.get("updated"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "arxiv_base_id": self.arxiv_base_id,
            "seen_version": self.seen_version,
            "seen_at": self.seen_at,
            "updated": self.updated,
        }
