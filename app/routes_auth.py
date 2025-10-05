# app/routes_auth.py
from fastapi import APIRouter, HTTPException, Depends, Response, Request
from pydantic import BaseModel
from jose import JWTError

from app.users import UserCreate, create_user, verify_user, get_user
from app.security.auth import (
    create_access_token,
    create_refresh_token,
    _decode_required,
)
from app.security.settings import (
    RATE_LIMIT_LOGIN_MAX,
    RATE_LIMIT_LOGIN_WINDOW,
    COOKIE_DOMAIN,
    COOKIE_SECURE,
)
from app.security.ratelimit import rate_limit_login_dep
from app.security.passwords import validate_password
from app.security.session import revoke_refresh, is_refresh_active
from app.security.observability import record_auth_failure

router = APIRouter(tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

def _create_user_compat(body: UserCreate) -> None:
    """
    Tries both common create_user signatures:
      - create_user(UserCreate)
      - create_user(username, password, role)
    """
    try:
        return create_user(body)
    except TypeError:
        return create_user(body.username, body.password, body.role)

@router.post("/signup", response_model=dict)
def signup(body: UserCreate):
    # A07: password policy
    ok, msg = validate_password(body.password, body.username)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    try:
        _create_user_compat(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}

class Login(BaseModel):
    username: str
    password: str

def _set_refresh_cookie(resp: Response, refresh_token: str):
    resp.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        domain=COOKIE_DOMAIN,  # None → current host in dev
        path="/",
        max_age=60 * 60 * 24 * 30,  # UI hint; server still enforces JWT exp
    )

@router.post("/login", response_model=Token)
def login(
    body: Login,
    _rl=Depends(rate_limit_login_dep(RATE_LIMIT_LOGIN_MAX, RATE_LIMIT_LOGIN_WINDOW)),
):
    u = verify_user(body.username, body.password)
    if not u:
        record_auth_failure("invalid_credentials")
        record_auth_failure("expired_token")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(u.username, u.role)
    refresh = create_refresh_token(u.username)

    resp = Response(media_type="application/json")
    _set_refresh_cookie(resp, refresh)
    resp.body = (f'{{"access_token":"{access}","token_type":"bearer"}}').encode()
    return resp

@router.post("/refresh", response_model=Token)
def refresh(request: Request):
    rt = request.cookies.get("refresh_token")
    if not rt:
        raise HTTPException(status_code=401, detail="Missing refresh cookie")
    try:
        payload = _decode_required(rt)
        if payload.get("typ") != "refresh":
            raise HTTPException(status_code=401, detail="Wrong token type")
        jti = payload.get("jti")
        sub = payload.get("sub")
        if not jti or not sub or not is_refresh_active(jti):
            raise HTTPException(status_code=401, detail="Refresh revoked or expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh")

    # rotate: revoke old, issue new
    revoke_refresh(jti)
    user = get_user(sub)
    role = getattr(user, "role", "candidate")
    new_access = create_access_token(sub, role)
    new_refresh = create_refresh_token(sub)

    resp = Response(media_type="application/json")
    _set_refresh_cookie(resp, new_refresh)
    resp.body = (f'{{"access_token":"{new_access}","token_type":"bearer"}}').encode()
    return resp

@router.post("/logout", status_code=204)
def logout(request: Request, response: Response):
    # Try to revoke the current refresh JTI
    rt = request.cookies.get("refresh_token")
    if rt:
        try:
            payload = _decode_required(rt)
            jti = payload.get("jti")
            if jti:
                revoke_refresh(jti)
        except JWTError:
            pass

    # Clear the cookie on the SAME response object
    response.delete_cookie("refresh_token", domain=COOKIE_DOMAIN, path="/")
    response.status_code = 204   # <-- add this line
    return response
