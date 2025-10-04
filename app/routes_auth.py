# app/routes_auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from app.users import UserCreate, create_user, verify_user
from app.security.auth import create_access_token
from app.security.settings import RATE_LIMIT_LOGIN_MAX, RATE_LIMIT_LOGIN_WINDOW
from app.security.ratelimit import rate_limit_login_dep
from fastapi import Depends


router = APIRouter(tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/signup")
def signup(body: UserCreate):
    try:
        create_user(body)
    except ValueError:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"ok": True}

class Login(BaseModel):
    username: str
    password: str

@router.post("/login", response_model=Token)
def login(
    body: Login,
    _rl = Depends(rate_limit_login_dep(RATE_LIMIT_LOGIN_MAX, RATE_LIMIT_LOGIN_WINDOW)),
):
    u = verify_user(body.username, body.password)
    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Sign a JWT with username + role
    return Token(access_token=create_access_token(u.username, u.role))
