from fastapi import Depends, HTTPException, status
from .auth import get_current_user, User

def require_role(*roles: str):
    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return _dep

def owner_or_admin(owner_username: str, user: User) -> None:
    if user.role != "admin" and user.username != owner_username:
        raise HTTPException(status_code=403, detail="Forbidden (owner or admin only)")