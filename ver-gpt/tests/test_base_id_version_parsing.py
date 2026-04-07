import pytest

from arxiv_cli.api.utils import base_arxiv_id, parse_version


@pytest.mark.parametrize(
    "raw,base,ver",
    [
        ("2402.05964v2", "2402.05964", 2),
        ("2402.05964", "2402.05964", None),
        ("cs/0112017v1", "cs/0112017", 1),
    ],
)
def test_base_and_version(raw, base, ver):
    assert base_arxiv_id(raw) == base
    assert parse_version(raw) == ver
