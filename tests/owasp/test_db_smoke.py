from app.db.core import SessionLocal
from app.db.models import User

def test_db_smoke():
    db = SessionLocal()
    try:
        u = User(username="user_smoke", password_hash="hash", role="candidate")
        db.add(u)
        db.commit()
        db.refresh(u)
        assert u.id > 0
        # cleanup so the test can run again
        db.delete(u)
        db.commit()
    finally:
        db.close()
