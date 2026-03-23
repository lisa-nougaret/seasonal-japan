DROP TABLE IF EXISTS analytics.fact_sakura_prediction_features;

CREATE TABLE analytics.fact_sakura_prediction_features AS
WITH sakura_locations AS (
    SELECT DISTINCT
        LPAD(location_code::text, 3, '0') AS location_code
    FROM analytics.fact_sakura_events
    WHERE event_type = 'sakura_bloom'
),
forecast_year AS (
    SELECT MAX(EXTRACT(YEAR FROM date_key))::int AS year
    FROM analytics.fact_monthly_climate
),
station_climate AS (
    SELECT
        RIGHT(station_code::text, 3) AS location_code,
        date_key,
        mean_temp_c,
        precipitation_mm
    FROM analytics.fact_monthly_climate
),
climate_features AS (
    SELECT
        sl.location_code,
        fy.year,
        AVG(
            CASE
                WHEN EXTRACT(MONTH FROM sc.date_key) IN (9, 10, 11)
                 AND EXTRACT(YEAR FROM sc.date_key) = fy.year - 1
                THEN sc.mean_temp_c
            END
        ) AS last_autumn_mean_temp,
        AVG(
            CASE
                WHEN (
                    EXTRACT(MONTH FROM sc.date_key) = 12
                    AND EXTRACT(YEAR FROM sc.date_key) = fy.year - 1
                )
                OR (
                    EXTRACT(MONTH FROM sc.date_key) IN (1, 2)
                    AND EXTRACT(YEAR FROM sc.date_key) = fy.year
                )
                THEN sc.mean_temp_c
            END
        ) AS winter_mean_temp,
        AVG(
            CASE
                WHEN EXTRACT(MONTH FROM sc.date_key) = 1
                 AND EXTRACT(YEAR FROM sc.date_key) = fy.year
                THEN sc.mean_temp_c
            END
        ) AS january_mean_temp,
        AVG(
            CASE
                WHEN EXTRACT(MONTH FROM sc.date_key) = 2
                 AND EXTRACT(YEAR FROM sc.date_key) = fy.year
                THEN sc.mean_temp_c
            END
        ) AS february_mean_temp,
        AVG(
            CASE
                WHEN EXTRACT(MONTH FROM sc.date_key) = 3
                 AND EXTRACT(YEAR FROM sc.date_key) = fy.year
                THEN sc.mean_temp_c
            END
        ) AS march_mean_temp,
        SUM(
            CASE
                WHEN EXTRACT(MONTH FROM sc.date_key) IN (1, 2, 3)
                 AND EXTRACT(YEAR FROM sc.date_key) = fy.year
                THEN sc.mean_temp_c
            END
        ) AS january_march_cumulative_temp,
        SUM(
            CASE
                WHEN (
                    EXTRACT(MONTH FROM sc.date_key) = 12
                    AND EXTRACT(YEAR FROM sc.date_key) = fy.year - 1
                )
                OR (
                    EXTRACT(MONTH FROM sc.date_key) IN (1, 2)
                    AND EXTRACT(YEAR FROM sc.date_key) = fy.year
                )
                THEN sc.precipitation_mm
            END
        ) AS winter_precipitation_mm
    FROM sakura_locations sl
    CROSS JOIN forecast_year fy
    LEFT JOIN station_climate sc
        ON sc.location_code = sl.location_code
    GROUP BY sl.location_code, fy.year
)
SELECT
    location_code,
    year,
    'sakura_bloom' AS event_type,
    last_autumn_mean_temp,
    winter_mean_temp,
    january_mean_temp,
    february_mean_temp,
    march_mean_temp,
    january_march_cumulative_temp,
    winter_precipitation_mm
FROM climate_features
WHERE
    last_autumn_mean_temp IS NOT NULL
    AND winter_mean_temp IS NOT NULL
    AND january_mean_temp IS NOT NULL
    AND february_mean_temp IS NOT NULL
    AND march_mean_temp IS NOT NULL
    AND january_march_cumulative_temp IS NOT NULL;