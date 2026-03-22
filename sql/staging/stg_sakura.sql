DROP TABLE IF EXISTS staging.stg_jma_sakura;

CREATE TABLE staging.stg_jma_sakura AS
SELECT
    station_code_raw AS location_code,
    TRIM(location_name_raw) AS location_name,
    year,
    CASE
        WHEN event_date_raw IS NULL THEN NULL
        WHEN TRIM(event_date_raw) ~ '^\d{1,2}-\d{1,2}$' THEN
            TO_DATE(year::text || '-' || TRIM(event_date_raw), 'YYYY-MM-DD')
        ELSE NULL
    END AS event_date,
    CASE
        WHEN event_date_raw IS NULL THEN NULL
        WHEN TRIM(event_date_raw) ~ '^\d{1,2}-\d{1,2}$' THEN
            EXTRACT(DOY FROM TO_DATE(year::text || '-' || TRIM(event_date_raw), 'YYYY-MM-DD'))::INT
        ELSE NULL
    END AS day_of_year,
    event_type,
    data_status,
    source_name,
    source_url,
    rm_raw,
    event_date_raw,
    raw_ingested_at
FROM raw.jma_sakura_raw;