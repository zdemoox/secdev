from __future__ import annotations

import time
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class HttpClientPolicy:
    timeout_seconds: float = 5.0
    connect_seconds: float = 3.0
    retries: int = 3
    backoff_base_seconds: float = 0.5


def get_with_policy(
    url: str, *, policy: HttpClientPolicy = HttpClientPolicy()
) -> httpx.Response:
    timeout = httpx.Timeout(
        policy.timeout_seconds,
        connect=policy.connect_seconds,
        read=policy.timeout_seconds,
    )

    for attempt in range(policy.retries):
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                resp = client.get(url)
                resp.raise_for_status()
                return resp
        except Exception:
            if attempt == policy.retries - 1:
                raise
            time.sleep(policy.backoff_base_seconds * (attempt + 1))

    raise RuntimeError("unreachable")
