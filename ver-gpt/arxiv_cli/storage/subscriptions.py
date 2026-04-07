from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from arxiv_cli.config.paths import get_paths
from arxiv_cli.storage.schema import now_iso


@dataclass
class Subscription:
    id: str
    query: str
    categories: list[str]
    created_at: str

    @classmethod
    def create(cls, *, query: str, categories: list[str]) -> "Subscription":
        sid = uuid4().hex[:10]
        return cls(id=sid, query=query, categories=categories, created_at=now_iso())

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Subscription":
        return cls(
            id=str(d["id"]),
            query=str(d.get("query", "")),
            categories=list(d.get("categories", [])),
            created_at=str(d.get("created_at") or d.get("createdAt") or now_iso()),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "query": self.query,
            "categories": self.categories,
            "created_at": self.created_at,
        }


class SubscriptionsStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = path or get_paths().subscriptions_path

    def load(self) -> list[Subscription]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("subscriptions.json must be a JSON list")
        return [Subscription.from_dict(x) for x in data]

    def save(self, subs: list[Subscription]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([s.to_dict() for s in subs], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def add(self, sub: Subscription) -> None:
        subs = self.load()
        subs.append(sub)
        self.save(subs)

    def remove(self, sub_id: str) -> bool:
        subs = self.load()
        kept = [s for s in subs if s.id != sub_id]
        if len(kept) == len(subs):
            return False
        self.save(kept)
        return True


class SubscriptionsState:
    """Keeps last-seen ids per subscription.

    File format: JSON object {sub_id: {"seen_ids": [...], "last_checked_at": "..."}}
    """

    def __init__(self, path: Optional[Path] = None):
        self.path = path or (get_paths().state_dir / "subscriptions_state.json")

    def load(self) -> dict[str, dict[str, Any]]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("subscriptions_state.json must be a JSON object")
        return data

    def save(self, data: dict[str, dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def get_seen(self, sub_id: str) -> set[str]:
        data = self.load()
        entry = data.get(sub_id, {})
        return set(entry.get("seen_ids", []))

    def set_seen(self, sub_id: str, seen_ids: set[str]) -> None:
        data = self.load()
        entry = data.get(sub_id, {})
        entry["seen_ids"] = sorted(seen_ids)
        entry["last_checked_at"] = now_iso()
        data[sub_id] = entry
        self.save(data)

    def remove(self, sub_id: str) -> None:
        data = self.load()
        if sub_id in data:
            del data[sub_id]
            self.save(data)
