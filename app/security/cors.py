from starlette.middleware.cors import CORSMiddleware
from .settings import ALLOWED_ORIGINS

def add_cors(app):
    allow = ALLOWED_ORIGINS or ["http://127.0.0.1:5173","http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:3000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow,
        allow_credentials=True,
        allow_methods=["GET","POST","PUT","DELETE","OPTIONS"],
        allow_headers=["Authorization","Content-Type"],
    )