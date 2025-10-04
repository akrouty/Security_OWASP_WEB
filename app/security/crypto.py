# app/security/crypto.py
from __future__ import annotations
import structlog

def secret_strength_ok(secret: str) -> tuple[bool, str]:
    if not secret:
        return False, "SECRET_KEY is empty"
    if secret.startswith("dev-unsafe") or secret.startswith("dev-change-me"):
        return False, "SECRET_KEY uses a default/dev value"
    if len(secret) < 32:
        return False, "SECRET_KEY must be at least 32 characters"
    return True, "ok"

def enforce_secret_strength(secret: str, env: str,strict: bool = False) -> None:
    """
    In prod: weak secret -> crash startup.
    In dev: weak secret -> log a warning (so you notice but can keep working).
    """
    ok, msg = secret_strength_ok(secret)
    log = structlog.get_logger()
    if strict or env == "prod":
        if not ok:
            raise RuntimeError(msg)
    else:
        if not ok:
            log.warning("weak_secret_in_dev", message=msg)
