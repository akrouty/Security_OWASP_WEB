from fastapi import FastAPI
from app.security.headers import security_headers
from app.security.cors import add_cors
from app.security.logging import setup_logging, RequestIDMiddleware
from app.routes_auth import router as auth_router
from app.routes_bac import router as bac_router
from app.routes_apps import private as apps_router
from app.security.settings import APP_ENV, SECRET_KEY,STRICT_SECRETS
from app.security.crypto import enforce_secret_strength
from app.db.bootstrap import init_db
from app.security.limits import BodySizeLimit
from app.security.settings import BODY_MAX_BYTES
from app.router_dbg import router as debug_router

setup_logging()
enforce_secret_strength(SECRET_KEY, APP_ENV, strict=STRICT_SECRETS)
init_db()
app = FastAPI(title="OWASP Top 10 Starter")
app.add_middleware(BodySizeLimit, max_body_bytes=BODY_MAX_BYTES)

# Middlewares
app.middleware("http")(security_headers)
app.add_middleware(RequestIDMiddleware)
add_cors(app)

# ✅ Register routers 
app.include_router(auth_router)
app.include_router(bac_router)
app.include_router(debug_router)

app.include_router(apps_router)

@app.get("/health")
def health():
    return {"ok": True, "service": "api", "status": "healthy"}
