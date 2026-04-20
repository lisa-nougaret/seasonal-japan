-- Check row count
SELECT COUNT(*) AS row_count
FROM analytics.fact_sakura_forecast;

-- Check duplicate rows based on business key
SELECT
    location_code,
    forecast_year,
    event_type,
    model_name,
    model_version,
    COUNT(*) AS duplicate_count
FROM analytics.fact_sakura_forecast
GROUP BY
    location_code,
    forecast_year,
    event_type,
    model_name,
    model_version
HAVING COUNT(*) > 1;

-- Check null values in critical columns
SELECT
    SUM(CASE WHEN location_code IS NULL THEN 1 ELSE 0 END) AS null_location_code,
    SUM(CASE WHEN forecast_year IS NULL THEN 1 ELSE 0 END) AS null_forecast_year,
    SUM(CASE WHEN event_type IS NULL THEN 1 ELSE 0 END) AS null_event_type,
    SUM(CASE WHEN model_name IS NULL THEN 1 ELSE 0 END) AS null_model_name,
    SUM(CASE WHEN model_version IS NULL THEN 1 ELSE 0 END) AS null_model_version,
    SUM(CASE WHEN predicted_day_of_year IS NULL THEN 1 ELSE 0 END) AS null_predicted_day_of_year,
    SUM(CASE WHEN predicted_event_date IS NULL THEN 1 ELSE 0 END) AS null_predicted_event_date,
    SUM(CASE WHEN is_best_model IS NULL THEN 1 ELSE 0 END) AS null_is_best_model
FROM analytics.fact_sakura_forecast;

-- Check predicted day range
SELECT
    MIN(predicted_day_of_year) AS min_predicted_day,
    MAX(predicted_day_of_year) AS max_predicted_day
FROM analytics.fact_sakura_forecast;

-- Check suspiciously early or late predictions (e.g., before day 30 or after day 160)
SELECT
    location_code,
    forecast_year,
    model_name,
    predicted_day_of_year,
    predicted_event_date,
    is_best_model
FROM analytics.fact_sakura_forecast
WHERE predicted_day_of_year < 30 
    OR predicted_day_of_year > 160
ORDER BY predicted_day_of_year;