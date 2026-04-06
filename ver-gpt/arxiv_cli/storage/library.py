from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class LibraryItem:
    arxiv_id: str
    title: str
    authors: list[str]
    categories: list[str]
    published: Optional[str]  # ISO date-time string
    tags: list[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "LibraryItem":
        return cls(
            arxiv_id=d["arxiv_id"],
            title=d.get("title", ""),
            authors=list(d.get("authors", [])),
            categories=list(d.get("categories", [])),
            published=d.get("published"),
            tags=list(d.get("tags", [])),
        )


class Library:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[LibraryItem]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Library file must be a JSON list")
        return [LibraryItem.from_dict(x) for x in data]


def default_library_path() -> Path:
    # Minimal default: keep library in current working directory.
    # Later we can move to OS config dirs.
    return Path(".arxiv-cli-library.json")
