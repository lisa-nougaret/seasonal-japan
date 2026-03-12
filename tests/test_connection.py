from sqlalchemy import text
from src.db.db import get_engine

engine = get_engine()

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT current_database(), current_user, current_schema();")
    )
    for row in result:
        print(row)