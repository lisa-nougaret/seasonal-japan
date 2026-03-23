# To run the script: python -m src.features.run_sakura_forecast

import pandas as pd
from sqlalchemy import text
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
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

def load_training_data():
    query = """
    SELECT *
    FROM analytics.fact_sakura_training_features
    WHERE event_type = 'sakura_bloom'
    """
    engine = get_engine()
    return pd.read_sql(query, engine)

def train_model(df):
    X = df[FEATURES]
    y = df[TARGET]

    model = LinearRegression()
    model.fit(X, y)

    preds = model.predict(X)

    metrics = {
        "mae_days": mean_absolute_error(y, preds),
        "rmse_days": root_mean_squared_error(y, preds),
        "r2_score": r2_score(y, preds),
        "training_row_count": len(df),
    }

    return model, metrics

def load_prediction_features():
    query = """
    SELECT *
    FROM analytics.fact_sakura_prediction_features
    WHERE event_type = 'sakura_bloom'
    """
    engine = get_engine()
    df = pd.read_sql(query, engine)

    print(f"Prediction rows: {len(df)}")
    if not df.empty:
        print(df.head())

    return df

def build_predictions(df, model, metrics):
    pred_doy = model.predict(df[FEATURES]).round().astype(int)

    out = df[["location_code", "year", "event_type"]].copy()

    out["predicted_day_of_year"] = pred_doy

    out["predicted_event_date"] = pd.to_datetime(
        out["year"].astype(str) + "-01-01"
    ) + pd.to_timedelta(out["predicted_day_of_year"] - 1, unit="D")

    out["model_name"] = MODEL_NAME
    out["model_version"] = MODEL_VERSION
    out["training_row_count"] = metrics["training_row_count"]
    out["rmse_days"] = metrics["rmse_days"]
    out["mae_days"] = metrics["mae_days"]
    out["r2_score"] = metrics["r2_score"]
    out["prediction_status"] = "predicted"
    out["source_name"] = "model_linear_regression"

    out = out.rename(columns={"year": "forecast_year"})

    return out

def save_predictions(df):
    engine = get_engine()

    delete_sql = text("""
        DELETE FROM analytics.fact_sakura_forecast
        WHERE model_name = :model_name
          AND model_version = :model_version
    """)

    with engine.begin() as conn:
        conn.execute(delete_sql, {
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION
        })

    df.to_sql(
        "fact_sakura_forecast",
        engine,
        schema="analytics",
        if_exists="append",
        index=False
    )

def main():
    print("Loading training data...")
    train_df = load_training_data()

    if train_df.empty:
        print("No training data found.")
        return

    print("Training model...")
    model, metrics = train_model(train_df)

    print("Loading prediction features...")
    pred_df = load_prediction_features()

    if pred_df.empty:
        print("No prediction rows found.")
        return

    print("Building predictions...")
    predictions = build_predictions(pred_df, model, metrics)

    print("Saving predictions...")
    save_predictions(predictions)

    print("Done.")
    print(metrics)


if __name__ == "__main__":
    main()