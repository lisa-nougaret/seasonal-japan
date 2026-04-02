from pathlib import Path
from sqlalchemy import text
from src.db.db import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]

SQL_MODEL_FILES = [
    BASE_DIR / "sql" / "staging" / "stg_monthly_climate.sql",
    BASE_DIR / "sql" / "staging" / "stg_sakura.sql",

    BASE_DIR / "sql" / "marts" / "dim_date.sql",
    BASE_DIR / "sql" / "marts" / "dim_month.sql",
    BASE_DIR / "sql" / "marts" / "dim_station.sql",
    BASE_DIR / "sql" / "marts" / "dim_location.sql",

    BASE_DIR / "sql" / "marts" / "fact_monthly_climate.sql",
    BASE_DIR / "sql" / "marts" / "fact_sakura_events.sql",
    BASE_DIR / "sql" / "marts" / "fact_sakura_training_features.sql",
    BASE_DIR / "sql" / "marts" / "fact_sakura_prediction_features.sql",
]

def run_pipeline():
    engine = get_engine()

    with engine.begin() as conn:
        for sql_file in SQL_MODEL_FILES:
            print(f"Running {sql_file.relative_to(BASE_DIR)} ...")
            sql = sql_file.read_text(encoding="utf-8")
            conn.execute(text(sql))

    print("SQL pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()