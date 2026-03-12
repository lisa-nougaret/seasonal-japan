DROP TABLE IF EXISTS analytics.dim_station;
CREATE TABLE analytics.dim_station AS
SELECT station_code,
    station_name,
    MIN(month_start_date) AS first_observation,
    MAX(month_start_date) AS last_observation,
    COUNT(*) AS record_count
FROM staging.stg_jma_monthly_climate
GROUP BY station_code,
    station_name
ORDER BY station_code;