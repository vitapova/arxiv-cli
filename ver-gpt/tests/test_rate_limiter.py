import time

from arxiv_cli.api.rate_limit import RateLimiter


def test_rate_limiter_sleeps(monkeypatch):
    slept = {"total": 0.0}

    def fake_sleep(x: float) -> None:
        slept["total"] += x

    t = {"now": 0.0}

    def fake_monotonic() -> float:
        return t["now"]

    monkeypatch.setattr(time, "sleep", fake_sleep)
    monkeypatch.setattr(time, "monotonic", fake_monotonic)

    rl = RateLimiter(min_interval_s=3.0)

    # First call: last_ts=0 -> may sleep 3s (because dt=0)
    rl._last_ts = 0.0
    rl.sleep_if_needed()
    assert slept["total"] == 3.0

    # Move time forward 2 seconds since last_ts (which is set to monotonic() = 0.0)
    t["now"] = 2.0
    rl.sleep_if_needed()
    assert slept["total"] == 4.0

    # Move time forward enough
    t["now"] = 10.0
    rl.sleep_if_needed()
    assert slept["total"] == 4.0
