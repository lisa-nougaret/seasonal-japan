SELECT
    location_name,
    event_date,
    year,
    event_type, -- Only first bloom for now, can add full bloom later
    day_of_year,
    data_status,
    source_name
FROM staging.stg_jma_sakura;