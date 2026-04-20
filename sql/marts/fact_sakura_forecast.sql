DROP TABLE IF EXISTS analytics.fact_sakura_forecast;

CREATE TABLE analytics.fact_sakura_forecast (
    location_code TEXT NOT NULL,
    forecast_year INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    predicted_day_of_year INTEGER NOT NULL,
    predicted_event_date DATE NOT NULL,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    is_best_model BOOLEAN NOT NULL DEFAULT FALSE,
    trained_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    training_row_count INTEGER,
    rmse_days NUMERIC,
    mae_days NUMERIC,
    r2_score NUMERIC,
    prediction_status TEXT NOT NULL,
    source_name TEXT,
    PRIMARY KEY (location_code, forecast_year, event_type, model_version, model_name)
);