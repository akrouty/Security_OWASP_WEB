from pathlib import Path
import re

def test_requirements_are_pinned():
    req = Path("requirements.txt").read_text().splitlines()
    bad = []
    for i, line in enumerate(req, start=1):
        s = line.strip()
        if not s or s.startswith(("#", "--hash=")):
            continue
        if s.startswith(("-", "--")):
            continue
        # Must use exact pin "package==version"
        if "==" not in s:
            bad.append((i, s))
        # Disallow wildcards and range specifiers
        if re.search(r"[><~*]", s):
            bad.append((i, s))
    assert not bad, f"Unpinned or ranged deps in requirements.txt: {bad}"
