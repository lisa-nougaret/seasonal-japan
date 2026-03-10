CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

DROP TABLE IF EXISTS staging.stg_jma_monthly_climate;

CREATE TABLE staging.stg_jma_monthly_climate AS
WITH base AS (
    SELECT
        TRIM(station_code) AS station_code,
        TRIM(station_name) AS station_name,
        year::integer AS year,
        month::integer AS month,
        MAKE_DATE(year::integer, month::integer, 1) AS month_start_date,
        mean_temp_c::numeric AS mean_temp_c,
        precipitation_mm::numeric AS precipitation_mm,
        source_url,
        raw_ingested_at
    FROM raw.jma_monthly_climate
    WHERE year IS NOT NULL
      AND month IS NOT NULL
      AND month BETWEEN 1 AND 12
),
deduped AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY station_code, year, month
            ORDER BY raw_ingested_at DESC
        ) AS rn
    FROM base
)
SELECT
    station_code,
    station_name,
    year,
    month,
    month_start_date,
    mean_temp_c,
    precipitation_mm,
    source_url,
    raw_ingested_at
FROM deduped
WHERE rn = 1;

SELECT *
FROM staging.stg_jma_monthly_climate
ORDER BY year, month
LIMIT 20;