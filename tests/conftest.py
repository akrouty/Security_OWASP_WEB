# tests/conftest.py
import sys, pathlib
import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.bootstrap import init_db
from app.db.core import engine, Base
from app.security.ratelimit import reset_rate_limits

@pytest.fixture(scope="session", autouse=True)
def _schema():
    init_db()                 # create tables once for the test session
    yield
    # optional cleanup:
    # Base.metadata.drop_all(bind=engine)
@pytest.fixture(autouse=True)
def _reset_rl_between_tests():
    reset_rate_limits("login:")
    yield
    reset_rate_limits("login:")