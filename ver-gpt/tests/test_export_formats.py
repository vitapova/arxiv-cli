from arxiv_cli.export.bibtex import bibtex_dump
from arxiv_cli.export.csl import csl_dump
from arxiv_cli.storage.schema import ArticleRecord


def test_bibtex_dump_contains_arxiv_fields():
    items = [
        ArticleRecord(
            arxiv_id="2402.05964v2",
            title="A Survey",
            authors=["Yehui Tang"],
            categories=["cs.CL"],
            published="2024-02-05T12:16:28+00:00",
            tags=["x"],
        )
    ]

    bib = bibtex_dump(items)
    assert "@misc" in bib
    assert "eprint = {2402.05964v2}" in bib
    assert "archivePrefix = {arXiv}" in bib
    assert "primaryClass = {cs.CL}" in bib


def test_csl_dump_is_json_array():
    items = [
        ArticleRecord(
            arxiv_id="2402.05964v2",
            title="A Survey",
            authors=["Yehui Tang"],
            categories=["cs.CL"],
            published="2024-02-05T12:16:28+00:00",
            tags=["x"],
        )
    ]

    csl = csl_dump(items)
    import json

    arr = json.loads(csl)
    assert isinstance(arr, list)
    assert arr[0]["id"] == "2402.05964v2"
    assert arr[0]["archive"] == "arXiv"
