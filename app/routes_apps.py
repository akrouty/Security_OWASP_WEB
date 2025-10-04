from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Body, Path
from pydantic import BaseModel, Field
from app.security.auth import get_current_user, User
from app.security.rbac import owner_or_admin

private = APIRouter(tags=["private"], dependencies=[Depends(get_current_user)])

class ApplicationIn(BaseModel):
    title: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=2, max_length=500)

class ApplicationOut(BaseModel):
    id: int
    title: str
    description: str
    owner: str  # username

APPLICATIONS: Dict[int, ApplicationOut] = {}
NEXT_ID = 1

def _create(owner: str, data: ApplicationIn) -> ApplicationOut:
    global NEXT_ID
    app = ApplicationOut(id=NEXT_ID, title=data.title, description=data.description, owner=owner)
    APPLICATIONS[NEXT_ID] = app
    NEXT_ID += 1
    return app

def _get(app_id: int) -> ApplicationOut | None:
    return APPLICATIONS.get(app_id)

@private.post("/applications", response_model=ApplicationOut)
def create_application(body: ApplicationIn = Body(...), user: User = Depends(get_current_user)):
    return _create(owner=user.username, data=body)

@private.get("/applications/{app_id}", response_model=ApplicationOut)
def get_application(app_id: int = Path(..., ge=1), user: User = Depends(get_current_user)):
    app = _get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    # 🔒 horizontal control: only owner or admin can read it
    owner_or_admin(app.owner, user)
    return app

@private.get("/applications", response_model=List[ApplicationOut])
def list_applications(user: User = Depends(get_current_user)):
    if user.role == "admin":
        return list(APPLICATIONS.values())
    return [a for a in APPLICATIONS.values() if a.owner == user.username]
