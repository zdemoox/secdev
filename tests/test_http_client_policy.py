import httpx

from app.security.http_client import HttpClientPolicy, get_with_policy


class DummyResponse:
    status_code = 200

    def raise_for_status(self):
        return None


def test_http_client_enforces_timeout(monkeypatch):
    captured = {}

    class DummyClient:
        def __init__(self, *, timeout, follow_redirects):
            captured["timeout"] = timeout
            captured["follow_redirects"] = follow_redirects

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url):
            return DummyResponse()

    monkeypatch.setattr(httpx, "Client", DummyClient)
    resp = get_with_policy(
        "https://example.com/health",
        policy=HttpClientPolicy(timeout_seconds=5.0, connect_seconds=3.0),
    )
    assert resp.status_code == 200
    assert captured["follow_redirects"] is True
    assert isinstance(captured["timeout"], httpx.Timeout)
