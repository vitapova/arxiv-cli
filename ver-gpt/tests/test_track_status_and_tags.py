from pathlib import Path

from arxiv_cli.storage.library import Library
from arxiv_cli.storage.schema import ArticleRecord


def test_track_status_set_via_storage(tmp_path: Path):
    lib = Library(tmp_path / "library.json")
    lib.save([ArticleRecord(arxiv_id="1", status="unread"), ArticleRecord(arxiv_id="2", status="read")])

    items = lib.load()
    for it in items:
        if it.arxiv_id == "1":
            it.status = "starred"  # type: ignore[assignment]
    lib.save(items)

    items2 = {it.arxiv_id: it for it in lib.load()}
    assert items2["1"].status == "starred"


def test_track_tags_add_remove_via_storage(tmp_path: Path):
    lib = Library(tmp_path / "library.json")
    lib.save([ArticleRecord(arxiv_id="1", tags=["a", "b"])])

    items = lib.load()
    it = items[0]
    tagset = set(it.tags)
    tagset.add("c")
    tagset.discard("a")
    it.tags = sorted(tagset)
    lib.save(items)

    it2 = lib.load()[0]
    assert it2.tags == ["b", "c"]
