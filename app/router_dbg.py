from fastapi import APIRouter, Body
from typing import Dict, Any

router = APIRouter(tags=["debug"])

@router.post("/debug/echojson")
def echojson(payload: Dict[str, Any] = Body(...)):
    # middleware will block if too big; this just echoes size
    return {"ok": True, "size": len(str(payload))}
