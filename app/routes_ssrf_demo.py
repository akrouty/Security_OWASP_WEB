# app/routes_ssrf_demo.py
from fastapi import APIRouter, HTTPException, Query
from app.security.ssrf import safe_http_get

router = APIRouter(tags=["ssrf-demo"])

@router.get("/fetch")
async def fetch(url: str = Query(..., min_length=5, max_length=2048)):
    # WARNING: demo only. In real code, prefer server-side integrations instead of proxying.
    try:
        r = await safe_http_get(url)
        # Return limited info to avoid leaking internal details
        return {"status": r.status_code, "length": len(r.content)}
    except HTTPException:
        raise
    except Exception:
        # Network/timeout/etc.
        raise HTTPException(status_code=502, detail="Upstream fetch failed")
