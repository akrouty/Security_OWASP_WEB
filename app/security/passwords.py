import re
from typing import Tuple

# at least 8 chars, 1 upper, 1 lower, 1 digit, 1 special
RE_UPPER = re.compile(r"[A-Z]")
RE_LOWER = re.compile(r"[a-z]")
RE_DIGIT = re.compile(r"\d")
RE_SPEC  = re.compile(r"[^\w\s]")

def validate_password(pw: str, username: str | None = None) -> Tuple[bool, str | None]:
    if len(pw) < 8:
        return False, "Password must be at least 8 characters"
    if not RE_UPPER.search(pw): return False, "Add at least one uppercase letter"
    if not RE_LOWER.search(pw): return False, "Add at least one lowercase letter"
    if not RE_DIGIT.search(pw): return False, "Add at least one digit"
    if not RE_SPEC.search(pw):  return False, "Add at least one special character"
    if username and username.lower() in pw.lower():
        return False, "Password must not contain the username"
    return True, None
