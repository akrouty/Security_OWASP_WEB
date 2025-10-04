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
