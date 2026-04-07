from pathlib import Path

from arxiv_cli.storage.history import VersionEvent
from arxiv_cli.storage.tracking import TrackingStore


def test_tracking_store_append_and_get(tmp_path: Path):
    store = TrackingStore(tmp_path / "tracking.json")

    e1 = VersionEvent(arxiv_base_id="2402.05964", seen_version=1, seen_at="2026-01-01T00:00:00+00:00")
    e2 = VersionEvent(arxiv_base_id="2402.05964", seen_version=2, seen_at="2026-01-02T00:00:00+00:00")
    e2_dup = VersionEvent(arxiv_base_id="2402.05964", seen_version=2, seen_at="2026-01-03T00:00:00+00:00")

    store.append(e1)
    store.append(e2)
    store.append(e2_dup)

    events = store.get("2402.05964")
    assert [e.seen_version for e in events] == [1, 2]
