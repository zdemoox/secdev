from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_payment_accepts_decimal_and_normalizes_utc():
    payload = {
        "amount": "10.50",
        "currency": "usd",
        "occurred_at": "2025-12-14T10:00:00+02:00",
    }
    r = client.post("/payments", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["amount"] == "10.50"
    assert body["currency"] == "USD"
    assert body["occurred_at"].startswith("2025-12-14T08:00:00")


def test_payment_rejects_extra_fields():
    payload = {
        "amount": "10.00",
        "currency": "USD",
        "occurred_at": "2025-12-14T10:00:00Z",
        "hacker": "1",
    }
    r = client.post("/payments", json=payload)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_payment_rejects_bad_currency_length():
    payload = {
        "amount": "10.00",
        "currency": "US",
        "occurred_at": "2025-12-14T10:00:00Z",
    }
    r = client.post("/payments", json=payload)
    assert r.status_code == 422
