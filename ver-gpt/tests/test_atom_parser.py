from pathlib import Path

from arxiv_cli.api.parser import parse_feed


def test_parse_feed_minimal():
    xml = Path("tests/fixtures/arxiv_feed_minimal.xml").read_text(encoding="utf-8")
    papers = parse_feed(xml)

    assert len(papers) == 1
    p = papers[0]
    assert p.arxiv_id == "2402.05964v2"
    assert "Transformer Compression" in p.title
    assert p.authors[:2] == ["Yehui Tang", "Yunhe Wang"]
    assert "cs.LG" in p.categories
    assert p.links["abs"].endswith("/abs/2402.05964v2")
    assert p.pdf_url.endswith("/pdf/2402.05964v2")
    assert p.published is not None
    assert p.updated is not None
