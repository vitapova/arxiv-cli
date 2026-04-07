from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from arxiv_cli.config.paths import get_paths
from arxiv_cli.storage.schema import ArticleRecord, now_iso


def _parse_version(arxiv_id: str) -> int | None:
    # 2402.05964v2 -> 2
    if "v" not in arxiv_id:
        return None
    try:
        return int(arxiv_id.rsplit("v", 1)[-1])
    except ValueError:
        return None


class Library:
    """JSON-based library storage.

    File format v1: a JSON array of objects (ArticleRecord-compatible).
    """

    def __init__(self, path: Path | None = None):
        self.path = path or get_paths().library_path

    def load(self) -> list[ArticleRecord]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Library file must be a JSON list")
        return [self._from_dict(x) for x in data]

    def save(self, items: list[ArticleRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [self._to_dict(it) for it in items]
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def upsert(self, rec: ArticleRecord) -> None:
        items = self.load()
        by_id = {it.arxiv_id: it for it in items}
        if rec.added_at is None:
            rec.added_at = now_iso()
        if rec.version is None:
            rec.version = _parse_version(rec.arxiv_id)
        by_id[rec.arxiv_id] = rec
        self.save(list(by_id.values()))

    def _from_dict(self, d: dict[str, Any]) -> ArticleRecord:
        # Back-compat with the earlier minimal schema (no status/added_at/summary/etc.)
        rec = ArticleRecord(
            arxiv_id=d["arxiv_id"],
            title=d.get("title", ""),
            summary=d.get("summary", ""),
            authors=list(d.get("authors", [])),
            categories=list(d.get("categories", [])),
            published=d.get("published"),
            updated=d.get("updated"),
            added_at=d.get("added_at") or d.get("addedAt"),
            status=d.get("status", "unread"),
            tags=list(d.get("tags", [])),
            links=dict(d.get("links", {})),
            version=d.get("version") or _parse_version(d.get("arxiv_id", "")),
        )
        if rec.added_at is None:
            rec.added_at = now_iso()
        return rec

    def _to_dict(self, rec: ArticleRecord) -> dict[str, Any]:
        return {
            "arxiv_id": rec.arxiv_id,
            "title": rec.title,
            "summary": rec.summary,
            "authors": rec.authors,
            "categories": rec.categories,
            "published": rec.published,
            "updated": rec.updated,
            "added_at": rec.added_at,
            "status": rec.status,
            "tags": rec.tags,
            "links": rec.links,
            "version": rec.version,
        }


def default_library_path() -> Path:
    # Kept for CLI backward compatibility; now points to global data dir.
    return get_paths().library_path
