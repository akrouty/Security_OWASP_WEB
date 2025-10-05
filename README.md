OWASP Top-10 Starter (FastAPI + Security Pack)

A FastAPI backend that demonstrates defenses for OWASP Top-10 (A01–A10) with tests, dependency audits, static checks, metrics, rate-limiting, and file-integrity verification. Use it as a secure starter or integrate parts of it into another backend.

1) Project layout (what lives where)
.
├─ app/
│  ├─ main.py                     # app factory, middleware, routes mount
│  ├─ routes_auth.py              # /signup /login /refresh /logout /me
│  ├─ users.py                    # demo in-memory users (replace with DB in prod)
│  └─ security/
│     ├─ settings.py              # centralized config (reads .env)
│     ├─ auth.py                  # JWT access/refresh, validation
│     ├─ passwords.py             # password policy checks
│     ├─ ratelimit.py             # login rate limiting
│     ├─ observability.py         # Prometheus metrics + request timing
│     ├─ integrity.py             # integrity manifest verification
│     └─ session.py               # refresh token “revocation list”
├─ assets/                        # example assets verified by integrity.json
│  └─ demo.txt
├─ tools/
│  └─ make_integrity.py           # (re)build integrity.json safely
├─ tests/                         # pytest suite (OWASP A01–A10)
├─ integrity.json                 # generated file checksums (do NOT edit)
├─ requirements.in                # human-edited deps
├─ requirements.txt               # pinned & hashed deps used by CI
├─ pip_audit.toml                 # pip-audit config
├─ .github/workflows/ci.yml       # CI: tests + pip-audit + bandit + integrity
└─ .env.example                   # template env file

2) Windows + VS Code quick start

Create venv & install deps

py -m venv .venv
.\.venv\Scripts\Activate
python -m pip install --upgrade pip
pip install -r requirements.txt


Create your .env from the template and set a strong SECRET_KEY

copy .env.example .env
# then edit .env and set strong values (see Section 5)


Generate a secret (example):

python -c "import secrets; print(secrets.token_urlsafe(64))"


(Optional but recommended) enable file-integrity check on startup

# rebuild integrity.json if assets changed
python tools\make_integrity.py

# then enforce it on run:
set INTEGRITY_MANIFEST=integrity.json
set STRICT_INTEGRITY=true


Run the API

uvicorn app.main:app --reload


Open:

Health: http://127.0.0.1:8000/health

Docs: http://127.0.0.1:8000/docs

3) Endpoints you care about

POST /signup – create user (enforces password policy)

POST /login – returns access token (JWT) and sets refresh cookie

POST /refresh – returns a new access token (rotates refresh)

POST /logout – revokes refresh server-side and clears cookie

GET /me – current user (requires Authorization: Bearer <access>)

GET /metrics – Prometheus metrics (requests, latency, auth failures, rate-limit hits)

GET /fetch?url= – safe outbound fetch with allow-list (A10 SSRF demo)

GET /health – health probe

4) Running tests & security checks (local)
pytest -q                  # unit/integration tests (OWASP coverage)
bandit -q -r app           # static analysis
pip-audit -r requirements.txt   # dependency CVE scan


CI runs the same checks on every push/PR.

5) What to change for production

Set these in .env (never commit secrets):

APP_ENV=prod
SECRET_KEY=<super long random value>
JWT_ISSUER=https://your-issuer
JWT_AUDIENCE=your-audience
ACCESS_MINUTES=30           # your session needs
REFRESH_DAYS=7              # your rotation policy
FRONTEND_ORIGINS=https://your-frontend.example
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname
RATE_LIMIT_LOGIN_MAX=5
RATE_LIMIT_LOGIN_WINDOW=60
INTEGRITY_MANIFEST=integrity.json
STRICT_INTEGRITY=true


Other prod notes:

HTTPS: run behind TLS; refresh cookie is HttpOnly, Secure, SameSite=strict.

CORS: restrict to your real frontend(s).

DB: replace app/users.py with real models/queries (SQLAlchemy/ORM or your IdP).
The tests and API contract stay the same.

/metrics: expose internally only (Prometheus scrape).

Integrity: keep INTEGRITY_MANIFEST + STRICT_INTEGRITY=true enabled.

6) What NOT to change

Don’t disable JWT verification of signature/exp/iss/aud.

Don’t weaken the password policy (unless risk-accepted).

Don’t edit integrity.json by hand → always run python tools/make_integrity.py.

Don’t set permissive CORS (*) in production.

Don’t commit real .env or secrets.

7) Dependency management

We keep two files:

requirements.in → human-edited

requirements.txt → pinned + hashes (CI uses this)

To update deps locally (optional):

pip install pip-tools
pip-compile --generate-hashes -o requirements.txt requirements.in
pip install -r requirements.txt


Commit both files when you change deps.

8) OWASP coverage (what this starter demonstrates)

A01 Broken Access Control – role-based checks + anti-IDOR in routes & tests.

A02 Cryptographic Failures – strong secret, JWT claims (iss/aud/exp) enforced.

A03 Injection – safe patterns, ORM-ready (no raw SQL in demo).

A04 Insecure Design – password policy, rate-limit on /login.

A05 Security Misconfiguration – security headers, strict CORS.

A06 Vulnerable/Outdated Components – pip-audit in CI, Dependabot ready.

A07 Identification & Authentication – access/refresh split, rotation, logout revocation.

A08 Software/Data Integrity – integrity.json + startup verification.

A09 Security Logging & Monitoring – structured logs + Prometheus /metrics.

A10 SSRF – allow-listed /fetch?url= route.

9) Typical integration plan for a real backend

Keep the security folder as-is (auth, passwords, ratelimit, integrity, observability).

Replace app/users.py with your real DB/IdP logic. Keep route contracts.

Wire your data models into routes_auth.py where we call create_user/verify_user.

Set .env for prod (Section 5), keep integrity & CI checks enabled.

Expose /metrics internally; keep CI green before merging to main.

10) Quick commands (copy/paste)
# run API
uvicorn app.main:app --reload

# run tests
pytest -q

# static & CVE checks
bandit -q -r app
pip-audit -r requirements.txt

# regenerate integrity manifest
python tools\make_integrity.py
