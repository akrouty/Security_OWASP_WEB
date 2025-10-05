from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv(override=True)

SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-unsafe-change-me")
ALGO: str = os.getenv("JWT_ALGO", "HS256")
ACCESS_MINUTES: int = int(os.getenv("ACCESS_MINUTES", "60"))
_frontends = os.getenv("FRONTEND_ORIGINS", "").split(",")
ALLOWED_ORIGINS: list[str] = [o.strip() for o in _frontends if o.strip()]
APP_ENV: str = os.getenv("APP_ENV", "dev").lower()
STRICT_SECRETS: bool = os.getenv("STRICT_SECRETS", "false").lower() in ("1","true","yes")
BODY_MAX_BYTES: int = int(os.getenv("BODY_MAX_BYTES", "1048576"))  # 1MB default
RATE_LIMIT_LOGIN_MAX: int = int(os.getenv("RATE_LIMIT_LOGIN_MAX", "5"))
RATE_LIMIT_LOGIN_WINDOW: int = int(os.getenv("RATE_LIMIT_LOGIN_WINDOW", "60"))  # seconds

# A07 settings
JWT_ISSUER: str = os.getenv("JWT_ISSUER", "owasp-top10-starter")
JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "owasp-top10-web")
REFRESH_DAYS: int = int(os.getenv("REFRESH_DAYS", "7"))
CLOCK_SKEW_SECONDS: int = int(os.getenv("CLOCK_SKEW_SECONDS", "60"))

# Cookie settings (dev safe defaults; tighten in prod)
COOKIE_DOMAIN: str | None = os.getenv("COOKIE_DOMAIN") or None  # e.g. "yourdomain.com"
COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"  # true in prod

# Comma-separated host allow-list (exact hosts or domain suffixes like ".example.com")
_out_hosts = os.getenv("OUTBOUND_ALLOW_HOSTS", "").split(",")
OUTBOUND_ALLOW_HOSTS: list[str] = [h.strip() for h in _out_hosts if h.strip()]

# Block requests to private/internal IPs (RFC1918, loopback, link-local, etc.)
OUTBOUND_BLOCK_PRIVATE: bool = os.getenv("OUTBOUND_BLOCK_PRIVATE", "true").lower() == "true"

# Allowed destination ports (comma list). Default http/https.
_out_ports = os.getenv("OUTBOUND_ALLOWED_PORTS", "80,443").split(",")
OUTBOUND_ALLOWED_PORTS: set[int] = {int(p) for p in _out_ports if p.strip().isdigit()}