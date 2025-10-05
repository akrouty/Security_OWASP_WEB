from __future__ import annotations
import time
from typing import Dict, Tuple

# jti -> (username, exp_epoch)
_REFRESH_STORE: Dict[str, Tuple[str, int]] = {}

def save_refresh(jti: str, username: str, exp_epoch: int) -> None:
    _REFRESH_STORE[jti] = (username, exp_epoch)

def revoke_refresh(jti: str) -> None:
    _REFRESH_STORE.pop(jti, None)

def is_refresh_active(jti: str) -> bool:
    rec = _REFRESH_STORE.get(jti)
    if not rec:
        return False
    username, exp = rec
    return int(time.time()) < exp
