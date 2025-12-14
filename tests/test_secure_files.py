from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 10


def test_upload_rejects_bad_type(tmp_path: Path):
    app = create_app(upload_dir=tmp_path)
    c = TestClient(app)

    r = c.post("/upload-image", files={"file": ("x.bin", b"not_an_image")})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "upload_rejected"
    assert r.json()["error"]["message"] == "bad_type"


def test_upload_rejects_too_big(tmp_path: Path):
    app = create_app(upload_dir=tmp_path)
    c = TestClient(app)

    big = PNG + (b"0" * (5_000_000))
    r = c.post("/upload-image", files={"file": ("x.png", big)})
    assert r.status_code == 400
    assert r.json()["error"]["message"] == "too_big"


def test_upload_stores_uuid_name(tmp_path: Path):
    app = create_app(upload_dir=tmp_path)
    c = TestClient(app)

    r = c.post("/upload-image", files={"file": ("nice.png", PNG)})
    assert r.status_code == 200
    name = r.json()["stored_as"]
    assert name.endswith(".png")
    assert (tmp_path / name).exists()
