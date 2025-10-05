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
