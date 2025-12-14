from fastapi.testclient import TestClient
from app.main import app, create_app


client = TestClient(app)


def test_not_found():
    r = client.get("/items/999")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_validation_error():
    r = client.post("/items", params={"name": ""})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_error_has_correlation_id():
    r = client.get("/items/999")
    assert r.json()["error"]["correlation_id"]
    assert r.headers["X-Request-Id"] == r.json()["error"]["correlation_id"]


def test_respects_provided_request_id():
    r = client.get("/items/999", headers={"X-Request-Id": "abc-123"})
    assert r.json()["error"]["correlation_id"] == "abc-123"
    assert r.headers["X-Request-Id"] == "abc-123"


def test_rate_limit():
    limited_app = create_app(rate_limit_max=2, rate_limit_window_seconds=60)
    c = TestClient(limited_app)
    assert c.get("/health").status_code == 200
    assert c.get("/health").status_code == 200
    r = c.get("/health")
    assert r.status_code == 429
