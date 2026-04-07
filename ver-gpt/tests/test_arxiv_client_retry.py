from urllib.error import HTTPError

import pytest

from arxiv_cli.api.client import ArxivClient, ArxivQuery


def test_client_retries_on_503(monkeypatch):
    calls = {"n": 0}

    class DummyResp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            # minimal feed
            return b"<?xml version='1.0'?><feed xmlns='http://www.w3.org/2005/Atom'></feed>"

    def fake_urlopen(req, timeout):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise HTTPError(url=req.full_url, code=503, msg="", hdrs=None, fp=None)
        return DummyResp()

    monkeypatch.setattr("arxiv_cli.api.client.urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda _s: None)

    c = ArxivClient(retries=2, backoff_s=0.0)
    papers = c.search(ArxivQuery(search_query="all:test"))
    assert papers == []
    assert calls["n"] == 3


def test_client_gives_up_after_retries(monkeypatch):
    def fake_urlopen(req, timeout):
        raise HTTPError(url=req.full_url, code=503, msg="", hdrs=None, fp=None)

    monkeypatch.setattr("arxiv_cli.api.client.urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda _s: None)

    c = ArxivClient(retries=1, backoff_s=0.0)
    with pytest.raises(HTTPError):
        c.search(ArxivQuery(search_query="all:test"))
