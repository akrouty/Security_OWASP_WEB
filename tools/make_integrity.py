# tools/make_integrity.py
import os, sys, json
here = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(here)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from app.security.integrety import sha256_of_file, _repo_root

DEFAULT_FILES = ["assets/demo.txt"]

def main(paths):
    base = _repo_root()
    files = paths or DEFAULT_FILES
    entries = []
    for rel in files:
        full = os.path.join(base, rel)
        if not os.path.exists(full):
            raise SystemExit(f"Missing file: {rel}")
        digest, size = sha256_of_file(full)
        entries.append({"path": rel, "sha256": digest, "bytes": size})
    out = os.path.join(base, "integrity.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"files": entries}, fh, indent=2)
    print(f"Wrote integrity.json with {len(entries)} file(s)")

if __name__ == "__main__":
    main(sys.argv[1:])
