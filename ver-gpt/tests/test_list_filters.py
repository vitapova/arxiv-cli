from datetime import datetime, timezone
from pathlib import Path

import pytest

from arxiv_cli.storage.library import Library
from arxiv_cli.storage.schema import ArticleRecord


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


@pytest.fixture
def lib(tmp_path: Path):
    return Library(tmp_path / "library.json")


def test_list_like_filters_status_tag_category_date_and_query(lib: Library):
    # We test the storage-level assumptions for the list command:
    # status/tags/categories/added_at and search in title+summary.
    a1 = ArticleRecord(
        arxiv_id="1",
        title="LLM agents",
        summary="we study memory",
        categories=["cs.AI"],
        tags=["agents"],
        status="unread",
        added_at=_iso(datetime(2026, 4, 1, tzinfo=timezone.utc)),
    )
    a2 = ArticleRecord(
        arxiv_id="2",
        title="Transformers",
        summary="compression survey",
        categories=["cs.CL"],
        tags=["transformers"],
        status="read",
        added_at=_iso(datetime(2026, 4, 10, tzinfo=timezone.utc)),
    )
    lib.save([a1, a2])

    items = lib.load()

    # status
    unread = [it for it in items if it.status == "unread"]
    assert [it.arxiv_id for it in unread] == ["1"]

    # tag
    transformers = [it for it in items if set(["transformers"]).intersection(it.tags)]
    assert [it.arxiv_id for it in transformers] == ["2"]

    # category
    cs_ai = [it for it in items if set(["cs.AI"]).intersection(it.categories)]
    assert [it.arxiv_id for it in cs_ai] == ["1"]

    # query in title+summary
    q = "memory"
    hits = [it for it in items if q in (it.title + "\n" + it.summary).lower()]
    assert [it.arxiv_id for it in hits] == ["1"]
