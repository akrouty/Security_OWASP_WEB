from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Literal
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from .settings import SECRET_KEY, ALGO, ACCESS_MINUTES

Role = Literal["admin","recruiter","candidate"]

class User(BaseModel):
    username: str
    role: Role

security = HTTPBearer()

def create_access_token(sub: str, role: Role, minutes: int | None = None) -> str:
    """Mint a JWT with a lifetime in MINUTES (default from settings)."""
    lifetime = minutes if minutes is not None else ACCESS_MINUTES
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=lifetime)).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def get_current_user(authorization = Depends(security)) -> User:
    token = authorization.credentials.strip().strip('"').strip("'")
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGO],
            options={"leeway": 60}  # tolerate 60s clock drift / boundary
        )
        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if not username or not role:
            raise JWTError("missing claims")
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid or expired token: {e}")
    return User(username=username, role=role)  # type: ignore[arg-type]
