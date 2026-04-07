import pytest

from arxiv_cli.api.utils import normalize_arxiv_id


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("2402.05964v2", "2402.05964v2"),
        ("2402.05964", "2402.05964"),
        ("https://arxiv.org/abs/2402.05964v2", "2402.05964v2"),
        ("http://arxiv.org/abs/2402.05964v2", "2402.05964v2"),
        ("https://arxiv.org/pdf/2402.05964v2.pdf", "2402.05964v2"),
        ("cs/0112017v1", "cs/0112017v1"),
    ],
)
def test_normalize_arxiv_id_ok(raw, expected):
    assert normalize_arxiv_id(raw) == expected


@pytest.mark.parametrize("raw", ["", "not-an-id", "2402", "1234.12x", "https://example.com/abs/1234"]) 
def test_normalize_arxiv_id_bad(raw):
    with pytest.raises(ValueError):
        normalize_arxiv_id(raw)
