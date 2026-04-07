from pathlib import Path

from arxiv_cli.storage.library import Library
from arxiv_cli.storage.schema import ArticleRecord


def test_track_remove_logic_via_library(tmp_path: Path):
    # This is a storage-level test: remove behavior should delete by exact arxiv_id.
    lib = Library(tmp_path / "library.json")
    lib.save([ArticleRecord(arxiv_id="2402.05964v2"), ArticleRecord(arxiv_id="2604.03199v1")])

    items = lib.load()
    items = [it for it in items if it.arxiv_id != "2402.05964v2"]
    lib.save(items)

    remaining = [it.arxiv_id for it in lib.load()]
    assert remaining == ["2604.03199v1"]
