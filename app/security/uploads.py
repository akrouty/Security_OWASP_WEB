from fastapi import UploadFile, HTTPException
try:
    import magic  # provided by python-magic-bin on Windows
except Exception:
    magic = None

MAX_BYTES = 10 * 1024 * 1024
SAFE_MIME = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

async def validate_upload(file: UploadFile, body: bytes):
    if len(body) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    if not magic:
        raise HTTPException(status_code=500, detail="MIME detector not available")
    mime = magic.from_buffer(body, mime=True)
    if mime not in SAFE_MIME:
        raise HTTPException(status_code=400, detail=f"Unsupported MIME: {mime}")