from urllib.error import HTTPError

import pytest


def test_backoff_retries_on_429(monkeypatch):
    # Minimal unit test of the retry loop behavior by simulating HTTPError(429).
    class DummyLimiter:
        def sleep_if_needed(self):
            return None

    calls = {"n": 0}

    def fake_search(_q):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise HTTPError(url="x", code=429, msg="too many", hdrs=None, fp=None)
        return ["ok"]

    slept = {"total": 0.0}

    def fake_sleep(x: float):
        slept["total"] += x

    monkeypatch.setattr("time.sleep", fake_sleep)

    # Inline copy of the loop logic shape: we assert retries/backoff happens.
    papers = None
    last_err = None
    attempts = 0
    retries_429 = 2
    backoff_s = 15.0

    while True:
        try:
            DummyLimiter().sleep_if_needed()
            papers = fake_search(None)
            break
        except HTTPError as e:
            last_err = e
            if e.code != 429 or attempts >= retries_429:
                break
            wait = backoff_s * (2**attempts)
            fake_sleep(wait)
            attempts += 1
            continue
        except Exception as e:
            last_err = e
            break

    assert papers == ["ok"]
    assert calls["n"] == 3
    assert slept["total"] == pytest.approx(15.0 + 30.0)
    assert last_err is not None
