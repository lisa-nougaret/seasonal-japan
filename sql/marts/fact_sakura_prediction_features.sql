DROP TABLE IF EXISTS analytics.fact_sakura_prediction_features;

CREATE TABLE analytics.fact_sakura_prediction_features AS
WITH sakura_locations AS (
    SELECT DISTINCT
        LPAD(location_code::text, 3, '0') AS location_code
    FROM analytics.fact_sakura_events
    WHERE event_type = 'sakura_bloom'
),
forecast_year AS (
    SELECT
        CASE
            WHEN EXTRACT(MONTH FROM CURRENT_DATE) >= 6
            THEN EXTRACT(YEAR FROM CURRENT_DATE)::int + 1
            ELSE EXTRACT(YEAR FROM CURRENT_DATE)::int
        END AS year
),
actual_months AS (
    SELECT
        RIGHT(station_code::text, 3) AS location_code,
        EXTRACT(YEAR FROM date_key)::int  AS year,
        EXTRACT(MONTH FROM date_key)::int AS month,
        mean_temp_c,
        precipitation_mm
    FROM analytics.fact_monthly_climate
),
historical_normals AS (
    SELECT
        RIGHT(station_code::text, 3)      AS location_code,
        EXTRACT(MONTH FROM date_key)::int AS month,
        AVG(mean_temp_c)                  AS avg_temp,
        AVG(precipitation_mm)             AS avg_precip
    FROM analytics.fact_monthly_climate
    WHERE EXTRACT(YEAR FROM date_key) BETWEEN 1991 AND 2020
    GROUP BY RIGHT(station_code::text, 3), EXTRACT(MONTH FROM date_key)
),
months_needed AS (
    SELECT
        sl.location_code,
        fy.year                                                        AS forecast_year,
        m.month,
        COALESCE(am.mean_temp_c,      hn.avg_temp)                    AS mean_temp_c,
        COALESCE(am.precipitation_mm, hn.avg_precip)                  AS precipitation_mm,
        (am.mean_temp_c IS NULL)                                       AS is_estimated
    FROM sakura_locations sl
    CROSS JOIN forecast_year fy
    CROSS JOIN (VALUES
        (9,  -1), (10, -1), (11, -1),
        (12, -1),
        (1,   0), (2,   0), (3,   0)
    ) AS m(month, year_offset)
    LEFT JOIN actual_months am
        ON  am.location_code = sl.location_code
        AND am.year          = fy.year + m.year_offset
        AND am.month         = m.month
    LEFT JOIN historical_normals hn
        ON  hn.location_code = sl.location_code
        AND hn.month         = m.month
)
SELECT
    location_code,
    forecast_year                                                          AS year,
    'sakura_bloom'                                                         AS event_type,
    AVG(CASE WHEN month IN (9, 10, 11) THEN mean_temp_c  END)            AS last_autumn_mean_temp,
    AVG(CASE WHEN month IN (12, 1, 2)  THEN mean_temp_c  END)            AS winter_mean_temp,
    AVG(CASE WHEN month = 1            THEN mean_temp_c  END)            AS january_mean_temp,
    AVG(CASE WHEN month = 2            THEN mean_temp_c  END)            AS february_mean_temp,
    AVG(CASE WHEN month = 3            THEN mean_temp_c  END)            AS march_mean_temp,
    SUM(CASE WHEN month IN (1, 2, 3)   THEN mean_temp_c  END)            AS january_march_cumulative_temp,
    SUM(CASE WHEN month IN (12, 1, 2)  THEN precipitation_mm END)        AS winter_precipitation_mm,
    BOOL_OR(is_estimated)                                                  AS using_climate_normals
FROM months_needed
GROUP BY location_code, forecast_year;
