from starlette.responses import Response


DOCS_PREFIXES = ("/docs", "/redoc")



def _csp_for_path(path: str) -> str:
    # Relaxed CSP for docs only (Swagger/Redoc use CDN + inline)
    if path.startswith(DOCS_PREFIXES):
        return (
            "default-src 'self'; "
            "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        )
    # Strict CSP for your app (tighten per your frontend needs later)
    return "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
async def security_headers(request, call_next):
    resp: Response = await call_next(request)
    resp.headers.update({
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Content-Security-Policy": _csp_for_path(request.url.path),
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
    })
    return resp


    # async def security_headers(request, call_next):
#     resp: Response = await call_next(request)
#     resp.headers.update({
#         "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
#         "Content-Security-Policy": "default-src 'self'",
#         "X-Frame-Options": "DENY",
#         "X-Content-Type-Options": "nosniff",
#         "Referrer-Policy": "no-referrer",
#     })
#     return resp

