from fastapi.testclient import TestClient

from app.main import app, create_app

client = TestClient(app)


def test_not_found_item():
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    assert "error" in body and body["error"]["code"] == "not_found"


def test_validation_error():
    r = client.post("/items", params={"name": ""})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"


def test_error_has_correlation_id_and_header():
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["correlation_id"]
    assert r.headers.get("X-Request-Id") == body["error"]["correlation_id"]


def test_respects_client_provided_request_id():
    provided = "test-correlation-123"
    r = client.get("/items/999", headers={"X-Request-Id": provided})
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["correlation_id"] == provided
    assert r.headers.get("X-Request-Id") == provided


def test_rate_limit_blocks_after_threshold():
    limited_app = create_app(rate_limit_max=2, rate_limit_window_seconds=60)
    c = TestClient(limited_app)

    assert c.get("/health").status_code == 200
    assert c.get("/health").status_code == 200
    r = c.get("/health")
    assert r.status_code == 429
    assert r.json()["error"]["code"] == "rate_limited"
