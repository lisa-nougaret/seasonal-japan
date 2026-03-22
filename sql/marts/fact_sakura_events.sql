DROP TABLE IF EXISTS analytics.fact_sakura_events;
CREATE TABLE analytics.fact_sakura_events AS
SELECT
    location_code,
    event_date AS date_key,
    year,
    event_type, -- Only first bloom for now, can add full bloom later
    day_of_year,
    data_status,
    source_name
FROM staging.stg_jma_sakura;