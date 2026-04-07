from datetime import date, datetime, timezone

from arxiv_cli.api.models import Paper
from arxiv_cli.digest.generator import build_digest, digest_to_markdown


def _p(arxiv_id: str, cat: str, published: str) -> Paper:
    dt = datetime.fromisoformat(published).astimezone(timezone.utc)
    return Paper(
        arxiv_id=arxiv_id,
        title=f"Title {arxiv_id}",
        summary=f"Summary {arxiv_id}",
        authors=["A"],
        categories=[cat],
        published=dt,
        updated=dt,
        links={"abs": f"https://arxiv.org/abs/{arxiv_id}", "pdf": f"https://arxiv.org/pdf/{arxiv_id}"},
    )


def test_build_digest_groups_by_primary_category_and_stats():
    papers = [
        _p("1", "cs.CL", "2026-04-01T00:00:00+00:00"),
        _p("2", "cs.CL", "2026-04-02T00:00:00+00:00"),
        _p("3", "cs.AI", "2026-04-03T00:00:00+00:00"),
    ]

    d = build_digest(papers, period="week", from_date=date(2026, 4, 1), to_date=date(2026, 4, 7))
    assert d.total == 3
    assert d.by_category["cs.CL"] == 2
    assert d.by_category["cs.AI"] == 1
    assert list(d.groups.keys())[0] == "cs.CL"  # most papers first


def test_digest_to_markdown_contains_sections():
    papers = [_p("1", "cs.CL", "2026-04-01T00:00:00+00:00")]
    d = build_digest(papers, period="day", from_date=date(2026, 4, 1), to_date=date(2026, 4, 2))
    md = digest_to_markdown(d, query_desc="cat:cs.CL")

    assert "# arXiv digest" in md
    assert "## Stats" in md
    assert "## Papers" in md
    assert "cs.CL" in md
    assert "Title 1" in md
