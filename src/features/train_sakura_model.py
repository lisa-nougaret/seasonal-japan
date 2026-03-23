from pathlib import Path
import pandas as pd
from sqlalchemy import text
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from src.db.db import get_engine

MODEL_NAME = "linear_regression"
MODEL_VERSION = "v1"

FEATURES = [
    "last_autumn_mean_temp",
    "winter_mean_temp",
    "january_mean_temp",
    "february_mean_temp",
    "march_mean_temp",
    "january_march_cumulative_temp",
]

TARGET = "day_of_year"

def load_training_data() -> pd.DataFrame:
    query = """
    SELECT
        location_code,
        year,
        event_type,
        event_date,
        day_of_year,
        last_autumn_mean_temp,
        winter_mean_temp,
        january_mean_temp,
        february_mean_temp,
        march_mean_temp,
        january_march_cumulative_temp,
        winter_precipitation_mm
    FROM analytics.fact_sakura_training_features
    WHERE event_type = 'sakura_bloom'
      AND day_of_year IS NOT NULL
      AND last_autumn_mean_temp IS NOT NULL
      AND winter_mean_temp IS NOT NULL
      AND january_mean_temp IS NOT NULL
      AND february_mean_temp IS NOT NULL
      AND march_mean_temp IS NOT NULL
      AND january_march_cumulative_temp IS NOT NULL
    """
    engine = get_engine()
    return pd.read_sql(query, engine)

def train_model(df: pd.DataFrame):
    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    metrics = {
        "mae_days": mean_absolute_error(y_test, preds),
        "rmse_days": root_mean_squared_error(y_test, preds),
        "r2_score": r2_score(y_test, preds),
        "training_row_count": len(X_train),
    }

    return model, metrics

def main():
    train_df = load_training_data()

    if train_df.empty:
        print("No training data found.")
        return

    model, metrics = train_model(train_df)

    print("Model trained successfully.")
    print(metrics)


if __name__ == "__main__":
    main()