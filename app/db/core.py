from __future__ import annotations
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Local dev DB (file). Later: switch to Postgres by changing this env var.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

class Base(DeclarativeBase):
    pass

# Needed for SQLite on Windows; harmless for Postgres to leave False.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, future=True, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
