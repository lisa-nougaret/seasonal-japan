DROP TABLE IF EXISTS analytics.fact_sakura_features;

CREATE TABLE analytics.fact_sakura_features AS
WITH sakura AS (
    SELECT
        LPAD(location_code::text, 3, '0') AS location_code,
        year,
        event_type,
        date_key AS event_date,
        day_of_year,
        data_status,
        source_name
    FROM analytics.fact_sakura_events
    WHERE date_key IS NOT NULL
        AND day_of_year IS NOT NULL
),
climate_joined AS (
    SELECT
        s.location_code,
        s.year,
        s.event_type,
        s.event_date,
        s.day_of_year,
        s.data_status,
        s.source_name,
        c.station_code,
        c.date_key,
        c.mean_temp_c,
        c.precipitation_mm
    FROM sakura s
    LEFT JOIN analytics.fact_monthly_climate c
        ON RIGHT(c.station_code::text, 3) = s.location_code
),
climate_features AS (
    SELECT
        location_code,
        year,
        AVG(
            CASE
                WHEN 
                    EXTRACT(MONTH FROM date_key) IN (9, 10, 11)
                    AND EXTRACT(YEAR FROM date_key) = year - 1
                THEN mean_temp_c
            END
        ) AS last_autumn_mean_temp,
        AVG(
            CASE
                WHEN (
                    EXTRACT(MONTH FROM date_key) = 12
                    AND EXTRACT(YEAR FROM date_key) = year - 1
                )
                OR (
                    EXTRACT(MONTH FROM date_key) IN (1, 2)
                    AND EXTRACT(YEAR FROM date_key) = year
                )
                THEN mean_temp_c
            END
        ) AS winter_mean_temp,
        AVG(
            CASE
                WHEN
                    EXTRACT(MONTH FROM date_key) = 1
                    AND EXTRACT(YEAR FROM date_key) = year
                THEN mean_temp_c
            END
        ) AS january_mean_temp,
        AVG(
            CASE
                WHEN
                    EXTRACT(MONTH FROM date_key) = 2
                    AND EXTRACT(YEAR FROM date_key) = year
                THEN mean_temp_c
            END
        ) AS february_mean_temp,
        AVG(
            CASE
                WHEN
                    EXTRACT(MONTH FROM date_key) = 3
                    AND EXTRACT(YEAR FROM date_key) = year
                THEN mean_temp_c
            END
        ) AS march_mean_temp,
        SUM(
            CASE
                WHEN EXTRACT(MONTH FROM date_key) IN (1, 2, 3)
                 AND EXTRACT(YEAR FROM date_key) = year
                THEN mean_temp_c
            END
        ) AS january_march_cumulative_temp,
        SUM(
            CASE
                WHEN (
                    EXTRACT(MONTH FROM date_key) = 12
                    AND EXTRACT(YEAR FROM date_key) = year - 1
                )
                OR (
                    EXTRACT(MONTH FROM date_key) IN (1, 2)
                    AND EXTRACT(YEAR FROM date_key) = year
                )
                THEN precipitation_mm
            END
        ) AS winter_precipitation_mm
    FROM climate_joined
    GROUP BY location_code, year
)

SELECT
    s.location_code,
    s.year,
    s.event_type,
    s.event_date,
    s.day_of_year,
    s.data_status,
    s.source_name,
    cf.last_autumn_mean_temp,
    cf.winter_mean_temp,
    cf.january_mean_temp,
    cf.february_mean_temp,
    cf.march_mean_temp,
    cf.january_march_cumulative_temp,
    cf.winter_precipitation_mm
FROM sakura s
LEFT JOIN climate_features cf
    ON s.location_code = cf.location_code
   AND s.year = cf.year
WHERE
    cf.last_autumn_mean_temp IS NOT NULL
    AND cf.winter_mean_temp IS NOT NULL
    AND cf.january_mean_temp IS NOT NULL
    AND cf.february_mean_temp IS NOT NULL
    AND cf.march_mean_temp IS NOT NULL;