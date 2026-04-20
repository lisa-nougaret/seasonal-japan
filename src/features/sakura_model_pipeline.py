from pathlib import Path
import json
from datetime import datetime

import joblib
import pandas as pd
from sqlalchemy import text, bindparam
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from src.db.db import get_engine
from src.features.sakura_model_config import (
    MODEL_VERSION,
    FEATURES,
    TARGET,
    CANDIDATE_MODELS,
    EVALUATION_METRIC
)

ARTIFACT_DIR = Path("artifacts/models")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

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

def load_prediction_features() -> pd.DataFrame:
    query = """
    SELECT
        location_code,
        year,
        event_type,
        last_autumn_mean_temp,
        winter_mean_temp,
        january_mean_temp,
        february_mean_temp,
        march_mean_temp,
        january_march_cumulative_temp,
        winter_precipitation_mm
    FROM analytics.fact_sakura_prediction_features
    WHERE event_type = 'sakura_bloom'
      AND last_autumn_mean_temp IS NOT NULL
      AND winter_mean_temp IS NOT NULL
      AND january_mean_temp IS NOT NULL
      AND february_mean_temp IS NOT NULL
      AND march_mean_temp IS NOT NULL
      AND january_march_cumulative_temp IS NOT NULL
    """
    engine = get_engine()
    return pd.read_sql(query, engine)

def validate_feature_columns(df: pd.DataFrame, features: list[str]) -> None:
    missing_cols = [col for col in features if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required feature columns: {missing_cols}")

    null_counts = df[features].isnull().sum()
    bad_cols = null_counts[null_counts > 0]
    if not bad_cols.empty:
        raise ValueError(
            f"Null values found in feature columns: {bad_cols.to_dict()}"
        )

def split_training_data(df: pd.DataFrame):
    validate_feature_columns(df, FEATURES)

    if TARGET not in df.columns:
        raise ValueError(f"Missing target column: {TARGET}")
    
    if df[TARGET].isnull().any():
        raise ValueError(f"Null values found in target column: {TARGET}")

    X = df[FEATURES]
    y = df[TARGET]

    return train_test_split(
        X, 
        y, 
        test_size=0.2, 
        random_state=42
    )

def build_model(model_name: str):
    hyperparameters = CANDIDATE_MODELS[model_name]["hyperparameters"]

    if model_name == "linear_regression":
        return LinearRegression(**hyperparameters)
    
    if model_name == "random_forest":
        return RandomForestRegressor(**hyperparameters)

    elif model_name == "hist_gradient_boosting":
        return HistGradientBoostingRegressor(**hyperparameters)

    raise ValueError(f"Unknown model name: {model_name}")

def train_model(model, X_train: pd.DataFrame, y_train: pd.Series):
        model.fit(X_train, y_train)
        return model

def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    preds = model.predict(X_test)

    return {
        "mae_days": float(mean_absolute_error(y_test, preds)),
        "rmse_days": float(mean_squared_error(y_test, preds) ** 0.5),
        "r2_score": float(r2_score(y_test, preds)),
        "evaluation_row_count": int(len(X_test)),
    }

def select_best_model(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> pd.DataFrame:
    rows = []

    for model_name in CANDIDATE_MODELS:
        model = build_model(model_name)
        trained_model = train_model(model, X_train, y_train)
        metrics = evaluate_model(trained_model, X_test, y_test)

        rows.append(
            {
                "model_name": model_name,
                "model_type": type(trained_model).__name__,
                "metrics": metrics,
                **metrics,
            }
        )

    results_df = (
        pd.DataFrame(rows)
        .sort_values(by=EVALUATION_METRIC, ascending=True)
        .reset_index(drop=True)
    )

    return results_df

def fit_final_model(df: pd.DataFrame, model_name: str):
    validate_feature_columns(df, FEATURES)

    if TARGET not in df.columns:
        raise ValueError(f"Missing target column: {TARGET}")
    
    if df[TARGET].isnull().any():
        raise ValueError(f"Null values found in target column: {TARGET}")

    X = df[FEATURES]
    y = df[TARGET]

    model = build_model(model_name)
    model.fit(X, y)
    return model

def build_predictions(
    pred_df: pd.DataFrame, 
    model, 
    model_name: str,
    metrics: dict, 
    training_row_count: int,
) -> pd.DataFrame:
    validate_feature_columns(pred_df, FEATURES)

    pred_doy = model.predict(pred_df[FEATURES]).round().astype(int)

    out = pred_df[["location_code", "year", "event_type"]].copy()
    out["predicted_day_of_year"] = pred_doy.clip(1, 366)

    out["predicted_event_date"] = (
        pd.to_datetime(out["year"].astype(str) + "-01-01")
        + pd.to_timedelta(out["predicted_day_of_year"] - 1, unit="D")
    )

    out["model_name"] = model_name
    out["model_version"] = MODEL_VERSION
    out["training_row_count"] = training_row_count
    out["rmse_days"] = metrics["rmse_days"]
    out["mae_days"] = metrics["mae_days"]
    out["r2_score"] = metrics["r2_score"]
    out["prediction_status"] = "predicted"
    out["source_name"] = f"model_{model_name}"
    out = out.rename(columns={"year": "forecast_year"})

    return out

def save_predictions(df: pd.DataFrame) -> None:
    if df.empty:
        return
    
    engine = get_engine()

    forecast_years = df["forecast_year"].drop_duplicates().tolist()
    model_name = df["model_name"].iloc[0]
    model_version = df["model_version"].iloc[0]
    event_type = df["event_type"].iloc[0]

    delete_sql = text("""
        DELETE FROM analytics.fact_sakura_forecast
        WHERE model_name = :model_name
          AND model_version = :model_version
          AND event_type = :event_type
          AND forecast_year IN :forecast_years
    """).bindparams(bindparam("forecast_years", expanding=True))

    with engine.begin() as conn:
        conn.execute(
            delete_sql,
            {
                "model_name": model_name,
                "model_version": model_version,
                "event_type": event_type,
                "forecast_years": forecast_years,
            },
        )

    df.to_sql(
        "fact_sakura_forecast",
        engine,
        schema="analytics",
        if_exists="append",
        index=False,
    )

def save_model_artifact(
    model, 
    model_name: str,
    metrics: dict, 
    training_row_count: int,
    selection_results: pd.DataFrame,
) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    model_path = ARTIFACT_DIR / f"sakura_{model_name}_{MODEL_VERSION}_{timestamp}.joblib"
    meta_path = ARTIFACT_DIR / f"sakura_{model_name}_{MODEL_VERSION}_{timestamp}.json"

    joblib.dump(model, model_path)

    metadata = {
        "model_name": model_name,
        "model_version": MODEL_VERSION,
        "features": FEATURES,
        "selection_metric": EVALUATION_METRIC,
        "metrics": metrics,
        "training_row_count": training_row_count,
        "selection_results": selection_results.to_dict(orient="records"),
        "saved_at_utc": timestamp,
    }

    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return model_path