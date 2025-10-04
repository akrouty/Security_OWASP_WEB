# app/db/bootstrap.py
from .core import engine, Base
from . import models  # <-- important: register models with Base

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
