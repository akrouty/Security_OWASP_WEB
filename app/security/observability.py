# app/security/observability.py
from __future__ import annotations
import time
from typing import Callable, Awaitable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog   # <-- add this

log = structlog.get_logger(__name__)  # <-- add this

# ---- Prometheus metrics ----
REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Count of HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "path"],
)

AUTH_FAILURES = Counter(
    "auth_failures_total",
    "Failed authentication attempts",
    ["reason"],  # e.g. invalid_credentials, expired_token, tampered_token
)

RATE_LIMIT_HITS = Counter(
    "rate_limit_hits_total",
    "Times a rate limit blocked a request",
    ["bucket"],  # e.g. login, global, ip
)

def record_auth_failure(reason: str) -> None:
    AUTH_FAILURES.labels(reason=reason).inc()

def record_rate_limit(bucket: str) -> None:
    RATE_LIMIT_HITS.labels(bucket=bucket).inc()

# ---- Middleware to time and count requests ----
async def metrics_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        return response
    finally:
        dur = time.perf_counter() - start
        path = request.url.path
        # Keep path cardinality stable: collapse IDs if needed
        if path.count("/") > 3:
            path = "/".join(path.split("/")[:3] + ["…"])

        REQUEST_LATENCY.labels(method=request.method, path=path).observe(dur)

        status = getattr(request.state, "forced_status", None)  # rarely used
        code = str(
            status
            or getattr(request, "response_status", None)
            or getattr(getattr(request, "response", None), "status_code", "")
            or "200"
        )

        # Best-effort fallback to app_state, but never crash
        try:
            code = str(request.app.router.default.app_state.get("last_status", code))
        except Exception as e:
            log.debug("observability_best_effort_request_status_failed", error=str(e))

        # Prefer real response status if available
        try:
            code = str(response.status_code)
        except Exception as e:
            log.debug("observability_best_effort_response_status_failed", error=str(e))

        REQUESTS_TOTAL.labels(method=request.method, path=path, status=code).inc()

# ---- /metrics endpoint ----
def metrics_endpoint():
    from fastapi import Response as FastAPIResponse
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
