DROP TABLE IF EXISTS analytics.fact_monthly_climate;
CREATE TABLE analytics.fact_monthly_climate AS
SELECT station_code,
    month_start_date AS date_key,
    mean_temp_c,
    precipitation_mm
FROM staging.stg_jma_monthly_climate;