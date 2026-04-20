from pathlib import Path
from sqlalchemy import text
from src.db.db import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]

SQL_CHECK_FILES = [
    BASE_DIR / "sql" / "checks" / "check_fact_monthly_climate.sql",
    BASE_DIR / "sql" / "checks" / "check_fact_sakura_events.sql",
    BASE_DIR / "sql" / "checks" / "check_sakura_raw.sql",
    BASE_DIR / "sql" / "checks" / "check_sakura_training_features.sql",
    BASE_DIR / "sql" / "checks" / "check_sakura_prediction_features.sql",
]

def run_checks():
    engine = get_engine()

    with engine.connect() as conn:
        for sql_file in SQL_CHECK_FILES:
            print(f"Running check {sql_file.relative_to(BASE_DIR)} ...")
            sql = sql_file.read_text(encoding="utf-8")
            result = conn.execute(text(sql))

            print("Result:")
            if result.returns_rows:
                rows = result.fetchall()
                for row in rows:
                    print(row)
            else:
                print("No rows returned.")

            print("-" * 60)

    print("All checks completed.")

if __name__ == "__main__":
    run_checks()