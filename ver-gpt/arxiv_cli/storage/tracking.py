from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from arxiv_cli.config.paths import get_paths
from arxiv_cli.storage.history import VersionEvent


class TrackingStore:
    """Store version history events per base arXiv id."""

    def __init__(self, path: Path | None = None):
        self.path = path or (get_paths().state_dir / "tracking.json")

    def load(self) -> dict[str, list[VersionEvent]]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("tracking.json must be a JSON object")
        out: dict[str, list[VersionEvent]] = {}
        for k, v in data.items():
            if not isinstance(v, list):
                continue
            out[k] = [VersionEvent.from_dict(x) for x in v]
        return out

    def save(self, d: dict[str, list[VersionEvent]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {k: [e.to_dict() for e in events] for k, events in d.items()}
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def append(self, event: VersionEvent) -> None:
        d = self.load()
        events = d.get(event.arxiv_base_id, [])
        # de-dupe by version
        if any(e.seen_version == event.seen_version for e in events):
            return
        events.append(event)
        events.sort(key=lambda e: e.seen_version)
        d[event.arxiv_base_id] = events
        self.save(d)

    def get(self, base_id: str) -> list[VersionEvent]:
        return self.load().get(base_id, [])
