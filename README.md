OWASP Top-10 Starter (FastAPI)
==================================================

Secure FastAPI backend covering OWASP A01–A10 with tests, rate-limiting, JWT (access/refresh), security headers/CORS, integrity checks, and Prometheus metrics.

Project structure (short)
------------------------
app/
  main.py                  - app init, middleware, routes
  routes_auth.py           - /signup /login /refresh /logout /me
  users.py                 - demo user store (replace with DB)
  security/
    settings.py            - reads .env (all config here)
    auth.py                - JWT create/verify, refresh rotation
    passwords.py           - password policy
    ratelimit.py           - login rate-limit
    observability.py       - /metrics, request timing/counters
    integrity.py           - integrity.json verification
    session.py             - refresh “revocation list”
assets/demo.txt
tools/make_integrity.py    - build integrity.json
tests/                     - pytest (OWASP checks)
integrity.json             - generated; do not edit by hand

Quick start (Windows / VS Code)
-------------------------------
1) Create and activate venv, install deps:
   py -m venv .venv
   .\.venv\Scripts\Activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt

2) Create .env and set strong SECRET_KEY:
   copy .env.example .env
   python -c "import secrets; print(secrets.token_urlsafe(64))"

3) (optional) rebuild integrity manifest if assets changed:
   python tools\make_integrity.py

4) Run the API:
   uvicorn app.main:app --reload
   Open http://127.0.0.1:8000/health and /docs

Core endpoints
--------------
- POST /signup (enforces password policy)
- POST /login → returns access token + sets refresh cookie
- POST /refresh → rotates refresh & returns new access token
- POST /logout → revokes refresh + clears cookie
- GET /me (Authorization: Bearer <access>)
- GET /metrics (Prometheus)
- GET /fetch?url= (SSRF-safe allowlist demo)
- GET /health

Required .env variables
-----------------------
APP_ENV=dev|prod
SECRET_KEY=<strong random>
JWT_ISSUER=https://your-issuer
JWT_AUDIENCE=your-audience
ACCESS_MINUTES=30
REFRESH_DAYS=7
FRONTEND_ORIGINS=https://your-frontend.example
DATABASE_URL=sqlite:///./dev.db
RATE_LIMIT_LOGIN_MAX=5
RATE_LIMIT_LOGIN_WINDOW=60
INTEGRITY_MANIFEST=integrity.json
STRICT_INTEGRITY=true

Tests & security checks
-----------------------
pytest -q
bandit -q -r app
pip-audit -r requirements.txt

Production changes (do)
-----------------------
- Set real DATABASE_URL and replace app/users.py with real DB/IdP logic
- Restrict FRONTEND_ORIGINS to real domains
- Keep STRICT_INTEGRITY=true and INTEGRITY_MANIFEST=integrity.json
- Run behind HTTPS (refresh cookie is HttpOnly, Secure, SameSite=strict)
- Expose /metrics internally only

Do NOT change
-------------
- JWT verification (signature/exp/iss/aud)
- Password policy without risk approval
- integrity.json by hand (always use tools/make_integrity.py)
- CORS '*' in prod
- Never commit real .env or secrets

CI (GitHub Actions)
-------------------
- .github/workflows/ci.yml runs tests, pip-audit, bandit
- Dependabot keeps dependencies up to date

Integration notes (for backend dev)
-----------------------------------
1) Keep app/security/* as-is
2) Swap app/users.py for real DB; keep routes_auth.py contracts
3) Configure .env as above; run tests → must be green
