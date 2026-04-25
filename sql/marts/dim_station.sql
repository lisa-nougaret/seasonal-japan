DROP TABLE IF EXISTS analytics.dim_station;

CREATE TABLE analytics.dim_station AS
SELECT
    c.station_code,
    (c.station_code::integer - 47000)::text AS location_code,
    c.station_name,
    m.latitude,
    m.longitude,
    MIN(c.month_start_date) AS first_observation,
    MAX(c.month_start_date) AS last_observation,
    COUNT(*) AS record_count
FROM staging.stg_jma_monthly_climate c
LEFT JOIN staging.stg_station_metadata m
    ON c.station_code::text = m.station_code::text
GROUP BY
    c.station_code,
    c.station_name,
    m.latitude,
    m.longitude
ORDER BY c.station_code;