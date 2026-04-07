from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class RateLimiter:
    """Simple in-process rate limiter (sequential use).

    Ensures at most 1 request per `min_interval_s`.
    """

    min_interval_s: float = 3.0
    _last_ts: float = 0.0

    def sleep_if_needed(self) -> None:
        now = time.monotonic()
        dt = now - self._last_ts
        wait = self.min_interval_s - dt
        if wait > 0:
            time.sleep(wait)
        self._last_ts = time.monotonic()
