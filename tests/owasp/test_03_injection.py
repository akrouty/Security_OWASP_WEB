import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.core import engine, SessionLocal
from app.security.sqlsafe import run_param_query
from app.security.validation import safe_join

# --------- a tiny temp schema just for tests ----------
@pytest.fixture(scope="module", autouse=True)
def seed_schema():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS candidates(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                title TEXT NOT NULL
            )
        """))
        conn.execute(text("DELETE FROM candidates"))
        conn.execute(text("""
            INSERT INTO candidates(name, title) VALUES
            ('Cyrine','Junior Python Dev'),
            ('Ahmed','Data Engineer'),
            ('Amine','Backend Engineer'),
            ('Nour','MLOps Engineer')
        """))
    yield
    # optional cleanup left out

@pytest.fixture
def db() -> Session:
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()

# --------- SQL injection test (parameterization) ----------
@pytest.mark.a03
def test_sql_injection_payload_is_neutralized(db: Session):
    # safe query: bind param (no string concat)
    sql = "SELECT id, name, title FROM candidates WHERE title LIKE :q"

    # normal search
    rows = run_param_query(db, sql, {"q": "%Engineer%"}).mappings().all()
    assert len(rows) >= 2  # at least Ahmed/Amine

    # classic injection payload should return 0, not all rows
    inj = "' OR 1=1 --"
    rows_inj = run_param_query(db, sql, {"q": f"%{inj}%"}).mappings().all()
    assert rows_inj == []  # treated as data, not code

# --------- Path traversal test ----------
@pytest.mark.a03
def test_path_traversal_is_blocked(tmp_path):
    base = tmp_path / "uploads"
    base.mkdir()
    # valid file under base
    good = safe_join(base, "resume.txt")
    assert str(good).startswith(str(base))

    # traversal attempts must fail
    with pytest.raises(ValueError):
        safe_join(base, "../.env")
    with pytest.raises(ValueError):
        safe_join(base, "../../etc/passwd")
