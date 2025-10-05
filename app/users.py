# app/users.py
from typing import Literal, Dict, Optional
from pydantic import BaseModel, Field
from passlib.hash import argon2

Role = Literal["admin", "recruiter", "candidate"]

class UserCreate(BaseModel):
    username: str
    password: str 
    role: Literal["admin","recruiter","candidate"]

class UserRecord(BaseModel):
    username: str
    password_hash: str
    role: Role

# in-memory store (lab only)
USERS: Dict[str, UserRecord] = {}

def create_user(data: UserCreate) -> None:
    if data.username in USERS:
        raise ValueError("exists")
    USERS[data.username] = UserRecord(
        username=data.username,
        password_hash=argon2.hash(data.password),
        role=data.role,
    )

def verify_user(username: str, password: str) -> Optional[UserRecord]:
    u = USERS.get(username)
    if not u:
        return None
    if not argon2.verify(password, u.password_hash):
        return None
    return u

def get_user(username: str) -> Optional[UserRecord]:
    return USERS.get(username)
