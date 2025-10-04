# app/routes_bac.py
from fastapi import APIRouter, Depends, HTTPException, Path
from app.security.auth import get_current_user, User
from app.security.rbac import require_role
from app.users import get_user, USERS

router = APIRouter(tags=["bac"])

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    # Authentication demo: who am I?
    return {"username": user.username, "role": user.role}

@router.get("/admin/stats")
def admin_stats(user: User = Depends(require_role("admin"))):
    # Vertical access control: admin only
    return {"users": len(USERS)}

@router.get("/users/{username}")
def user_profile(
    username: str = Path(..., min_length=3, max_length=32),
    user: User = Depends(get_current_user),
):
    # Horizontal access control (anti-IDOR): owner-or-admin
    if user.role != "admin" and user.username != username:
        raise HTTPException(status_code=403, detail="Forbidden (owner or admin only)")
    u = get_user(username)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    return {"username": u.username, "role": u.role}
