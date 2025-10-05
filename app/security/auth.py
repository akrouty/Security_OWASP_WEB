from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from pydantic import BaseModel

from .settings import (
    SECRET_KEY, ALGO, ACCESS_MINUTES,
    JWT_ISSUER, JWT_AUDIENCE, CLOCK_SKEW_SECONDS, REFRESH_DAYS
)
from .session import save_refresh  # is_refresh_active will be used in routes

Role = Literal["admin", "recruiter", "candidate"]

class User(BaseModel):
    username: str
    role: Role

security = HTTPBearer()

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def create_access_token(sub: str, role: str, minutes: int = ACCESS_MINUTES) -> str:
    now = _now_utc()
    payload = {
        "sub": sub,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "jti": str(uuid4()),
        "typ": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def create_refresh_token(sub: str) -> str:
    now = _now_utc()
    exp_dt = now + timedelta(days=REFRESH_DAYS)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int(exp_dt.timestamp()),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "jti": str(uuid4()),
        "typ": "refresh",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGO)
    # track active refresh by jti
    save_refresh(payload["jti"], sub, payload["exp"])
    return token

def _decode_required(token: str):
    # Enforce signature + exp + iss/aud (with small clock skew)
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGO],
        options={"verify_signature": True, "verify_exp": True},
        audience=JWT_AUDIENCE,
        issuer=JWT_ISSUER,
    )
    try:
        # Preferred path (python-jose supports leeway)
        return jwt.decode(token, leeway=CLOCK_SKEW_SECONDS, **base_kwargs)
    except TypeError:
        # Fallback if the decode() doesn't accept 'leeway'
        return jwt.decode(token, **base_kwargs)

def get_current_user(authorization = Depends(security)) -> User:
    token = authorization.credentials.strip().strip('"').strip("'")
    try:
        payload = _decode_required(token)
        if payload.get("typ") != "access":
            raise JWTError("wrong token type")
        username = payload.get("sub")
        role = payload.get("role")
        if not username or not role:
            raise JWTError("missing claims")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return User(username=username, role=role)  # type: ignore[arg-type]
