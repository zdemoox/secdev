import json
import os
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from app.security.files import secure_save_image
from app.security.http_client import HttpClientPolicy, get_with_policy


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


def _get_client_key(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def normalize_utc(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


class Payment(BaseModel):
    model_config = {"extra": "forbid"}

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    occurred_at: datetime


def create_app(
    *,
    rate_limit_max: int | None = None,
    rate_limit_window_seconds: int | None = None,
    upload_dir: Path | None = None,
) -> FastAPI:
    app = FastAPI(title="SecDev Course App", version="0.1.0")

    rl_max = rate_limit_max or int(os.getenv("RATE_LIMIT_MAX", "60"))
    rl_window = rate_limit_window_seconds or int(
        os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")
    )

    up_dir = upload_dir or Path(os.getenv("UPLOAD_DIR", "uploads"))
    up_dir.mkdir(parents=True, exist_ok=True)
    app.state.upload_dir = up_dir

    app.state.rate_limiter = {}
    app.state.rate_limit_max = rl_max
    app.state.rate_limit_window = rl_window

    @app.middleware("http")
    async def correlation_and_rate_limit(request: Request, call_next):
        cid = request.headers.get("X-Request-Id") or str(uuid4())
        request.state.correlation_id = cid

        key = _get_client_key(request)
        now = time.time()
        reset_ts, count = app.state.rate_limiter.get(
            key, (now + app.state.rate_limit_window, 0)
        )
        if now > reset_ts:
            reset_ts, count = (now + app.state.rate_limit_window, 0)

        if count >= app.state.rate_limit_max:
            payload = {
                "error": {
                    "code": "rate_limited",
                    "message": "too many requests",
                    "correlation_id": cid,
                }
            }
            resp = JSONResponse(status_code=429, content=payload)
            resp.headers["X-Request-Id"] = cid
            return resp

        app.state.rate_limiter[key] = (reset_ts, count + 1)
        response = await call_next(request)
        response.headers["X-Request-Id"] = cid
        return response

    def _error_payload(code: str, message: str, request: Request) -> dict:
        cid = getattr(request.state, "correlation_id", str(uuid4()))
        return {"error": {"code": code, "message": message, "correlation_id": cid}}

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status,
            content=_error_payload(exc.code, exc.message, request),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail if isinstance(exc.detail, str) else "http_error"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload("http_error", detail, request),
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content=_error_payload("validation_error", "invalid payload", request),
        )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    _DB = {"items": []}

    @app.post("/items")
    def create_item(name: str):
        if not name or len(name) > 100:
            raise ApiError(
                code="validation_error", message="name must be 1..100 chars", status=422
            )
        item = {"id": len(_DB["items"]) + 1, "name": name}
        _DB["items"].append(item)
        return item

    @app.get("/items/{item_id}")
    def get_item(item_id: int):
        for it in _DB["items"]:
            if it["id"] == item_id:
                return it
        raise ApiError(code="not_found", message="item not found", status=404)

    @app.post("/upload-image")
    async def upload_image(file: UploadFile):
        data = await file.read()
        try:
            path = secure_save_image(app.state.upload_dir, data)
        except ValueError as e:
            raise ApiError(code="upload_rejected", message=str(e), status=400) from e
        return {"stored_as": path.name}

    @app.post("/payments")
    async def create_payment(request: Request):
        raw = await request.body()
        try:
            payload = json.loads(raw.decode("utf-8"), parse_float=str)
        except Exception as e:
            raise ApiError(
                code="invalid_json", message="malformed json", status=400
            ) from e

        p = Payment.model_validate(payload)
        return {
            "amount": str(p.amount),
            "currency": p.currency.upper(),
            "occurred_at": normalize_utc(p.occurred_at).isoformat(),
        }

    @app.get("/external-health")
    def external_health(url: str):
        resp = get_with_policy(url, policy=HttpClientPolicy())
        return {"status_code": resp.status_code}

    return app


app = create_app()
