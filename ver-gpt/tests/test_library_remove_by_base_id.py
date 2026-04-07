from pathlib import Path

from arxiv_cli.storage.library import Library
from arxiv_cli.storage.schema import ArticleRecord


def test_remove_by_base_id_removes_all_versions(tmp_path: Path):
    lib = Library(tmp_path / "library.json")
    lib.save(
        [
            ArticleRecord(arxiv_id="2604.03199v1"),
            ArticleRecord(arxiv_id="2604.03199v2"),
            ArticleRecord(arxiv_id="other"),
        ]
    )

    removed = lib.remove_by_base_id("2604.03199")
    assert removed == 2
    remaining = [it.arxiv_id for it in lib.load()]
    assert remaining == ["other"]
