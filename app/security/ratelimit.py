from __future__ import annotations
import time
from typing import Tuple
from fastapi import Request, HTTPException, status

# Simple in-memory sliding window. In prod, prefer Redis.
_BUCKETS: dict[str, list[float]] = {}

def _allow(key: str, limit: int, window_s: int) -> Tuple[bool, int]:
    now = time.time()
    window_start = now - window_s
    bucket = _BUCKETS.setdefault(key, [])
    # drop old hits
    i = 0
    while i < len(bucket) and bucket[i] < window_start:
        i += 1
    if i:
        del bucket[:i]
    if len(bucket) < limit:
        bucket.append(now)
        return True, 0
    # compute retry-after
    retry_after = int(window_s - (now - bucket[0])) + 1
    return False, max(retry_after, 1)

def rate_limit_login_dep(limit: int, window_s: int):
    """
    Dependency for /login: rate-limit by client IP (simple & safe).
    """
    async def _dep(request: Request):
        client_ip = (request.client.host if request.client else "unknown")
        key = f"login:{client_ip}"
        ok, retry_after = _allow(key, limit, window_s)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts, slow down.",
                headers={"Retry-After": str(retry_after)},
            )
    return _dep
def reset_rate_limits(prefix: str | None = None) -> None:
    """Clear in-memory buckets. Use in tests to avoid cross-test pollution."""
    if prefix is None:
        _BUCKETS.clear()
        return
    for k in list(_BUCKETS.keys()):
        if k.startswith(prefix):
            _BUCKETS.pop(k, None)
