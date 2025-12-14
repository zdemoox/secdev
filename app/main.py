import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


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


def create_app(rate_limit_max: int = 60, rate_limit_window_seconds: int = 60) -> FastAPI:
    app = FastAPI(title="Study Planner API", version="0.1.0")

    app.state.rate_limiter = {}
    app.state.rate_limit_max = rate_limit_max
    app.state.rate_limit_window = rate_limit_window_seconds

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
            reset_ts, count = now + app.state.rate_limit_window, 0

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

    def error_payload(code: str, message: str, request: Request):
        cid = getattr(request.state, "correlation_id", str(uuid4()))
        return {"error": {"code": code, "message": message, "correlation_id": cid}}

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status,
            content=error_payload(exc.code, exc.message, request),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload("http_error", str(exc.detail), request),
        )

    _DB = {"items": []}

    @app.post("/items")
    def create_item(name: str):
        if not name or len(name) > 100:
            raise ApiError("validation_error", "name must be 1..100 chars", 422)
        item = {"id": len(_DB["items"]) + 1, "name": name}
        _DB["items"].append(item)
        return item

    @app.get("/items/{item_id}")
    def get_item(item_id: int):
        for it in _DB["items"]:
            if it["id"] == item_id:
                return it
        raise ApiError("not_found", "item not found", 404)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
