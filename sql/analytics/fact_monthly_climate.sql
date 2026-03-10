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

SELECT *
FROM analytics.fact_monthly_climate
LIMIT 10;

SELECT season, COUNT(*) AS records
FROM analytics.fact_monthly_climate
GROUP BY season
ORDER BY season;

SELECT quarter, COUNT(*) AS records
FROM analytics.fact_monthly_climate
GROUP BY quarter
ORDER BY quarter;

SELECT
    season,
    AVG(mean_temp_c) AS avg_temp_c
FROM analytics.fact_monthly_climate
GROUP BY season
ORDER BY season;

SELECT
    season,
    AVG(precipitation_mm) AS avg_precip_mm
FROM analytics.fact_monthly_climate
GROUP BY season
ORDER BY season;

SELECT
    COUNT(*) AS total_rows,
    COUNT(precipitation_mm) AS non_null_precipitation
FROM analytics.fact_monthly_climate;

SELECT
    COUNT(*) AS total_rows,
    COUNT(precipitation_mm) AS non_null_precipitation
FROM staging.stg_jma_monthly_climate;

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'staging'
  AND table_name = 'stg_jma_monthly_climate'
ORDER BY ordinal_position;

SELECT
    station_code,
    station_name,
    month_start_date,
    mean_temp_c,
    precipitation_mm
FROM staging.stg_jma_monthly_climate
LIMIT 20;