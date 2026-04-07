import json
from pathlib import Path

from arxiv_cli.storage.library import Library
from arxiv_cli.storage.schema import ArticleRecord


def test_library_upsert_roundtrip(tmp_path: Path):
    lib_path = tmp_path / "library.json"
    lib = Library(lib_path)

    rec = ArticleRecord(
        arxiv_id="2402.05964v2",
        title="Title",
        summary="Abstract",
        authors=["A One", "B Two"],
        categories=["cs.CL"],
        published="2024-02-05T12:16:28+00:00",
        updated="2024-04-07T13:03:58+00:00",
        added_at="2026-01-01T00:00:00+00:00",
        status="unread",
        tags=["t1"],
        links={"abs": "https://arxiv.org/abs/2402.05964v2"},
        version=2,
    )

    lib.upsert(rec)
    items = lib.load()
    assert len(items) == 1
    assert items[0].arxiv_id == rec.arxiv_id
    assert items[0].status == "unread"
    assert items[0].tags == ["t1"]

    # Ensure file is valid json list
    data = json.loads(lib_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert data[0]["arxiv_id"] == "2402.05964v2"
