-- Check the number of rows in the fact_sakura_events and staging tables -> should match

SELECT COUNT(*) AS fact_rows
FROM analytics.fact_sakura_events;

SELECT COUNT(*) AS staging_rows_with_date
FROM staging.stg_jma_sakura
WHERE event_date IS NOT NULL;

-- Check for duplicate records in the fact table based on location_code, year, and event_type

SELECT
    location_code,
    year,
    event_type,
    COUNT(*) AS records
FROM analytics.fact_sakura_events
GROUP BY location_code, year, event_type
HAVING COUNT(*) > 1
ORDER BY records DESC;

-- Check for missing values in the fact table

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE location_code IS NULL) AS missing_location_code,
    COUNT(*) FILTER (WHERE date_key IS NULL) AS missing_date_key,
    COUNT(*) FILTER (WHERE year IS NULL) AS missing_year,
    COUNT(*) FILTER (WHERE event_type IS NULL) AS missing_event_type,
    COUNT(*) FILTER (WHERE day_of_year IS NULL) AS missing_day_of_year
FROM analytics.fact_sakura_events;

-- Check for unmatched location codes in the fact table that do not exist in the dim_location table

SELECT COUNT(*) AS unmatched_locations
FROM analytics.fact_sakura_events f
LEFT JOIN analytics.dim_location d
    ON f.location_code = d.location_code
WHERE d.location_code IS NULL;

-- Same for date keys that do not exist in the dim_date table

SELECT COUNT(*) AS unmatched_dates
FROM analytics.fact_sakura_events f
LEFT JOIN analytics.dim_date d
    ON f.date_key = d.date_key
WHERE d.date_key IS NULL;