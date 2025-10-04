from __future__ import annotations
from typing import Any, Iterable, Mapping
from sqlalchemy import text
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session

def run_param_query(db: Session, sql: str, params: Mapping[str, Any]) -> Result:
    """
    Execute a SQL statement using **bind parameters**.
    Never concatenate user input into SQL strings.
    """
    # Example: sql="SELECT * FROM users WHERE email LIKE :q", params={"q": "%foo%"}
    return db.execute(text(sql), params)
