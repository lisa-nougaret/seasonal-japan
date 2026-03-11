DROP TABLE IF EXISTS analytics.fact_monthly_climate;

CREATE TABLE analytics.fact_monthly_climate AS
SELECT
    station_code,
    station_name,
    month_start_date,
    year,
    month,
    mean_temp_c,
    precipitation_mm,
    EXTRACT(QUARTER FROM month_start_date) AS quarter,
    CASE
        WHEN month IN (12, 1, 2) THEN 'winter'
        WHEN month IN (3, 4, 5) THEN 'spring'
        WHEN month IN (6, 7, 8) THEN 'summer'
        WHEN month IN (9, 10, 11) THEN 'autumn'
    END AS season
FROM staging.stg_jma_monthly_climate;