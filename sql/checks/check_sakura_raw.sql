-- Sakura raw data checks

-- Total rows
SELECT COUNT(*) AS total_rows
FROM staging.stg_jma_sakura;

-- Year range
SELECT
    MIN(year) AS min_year,
    MAX(year) AS max_year,
    COUNT(DISTINCT year) AS distinct_years
FROM staging.stg_jma_sakura;

-- Locations
SELECT
    COUNT(DISTINCT location_name) AS distinct_locations
FROM staging.stg_jma_sakura;

-- Missing dates
SELECT
    COUNT(*) AS missing_event_date
FROM staging.stg_jma_sakura
WHERE event_date_raw IS NULL;

-- Missing location names
SELECT
    location_name,
    COUNT(*) AS records
FROM staging.stg_jma_sakura
WHERE location_name IS NULL
GROUP BY location_name
ORDER BY records DESC, location_name
LIMIT 20;

-- Rows per year
SELECT
    year,
    COUNT(*) AS records
FROM staging.stg_jma_sakura
GROUP BY year
ORDER BY year;

-- Rows per event date
SELECT
    event_date_raw,
    COUNT(*) AS records
FROM staging.stg_jma_sakura
GROUP BY event_date_raw
ORDER BY records DESC, event_date_raw
LIMIT 30;

-- Data status distribution
SELECT
    source_name,
    source_url,
    data_status,
    COUNT(*) AS records
FROM staging.stg_jma_sakura
GROUP BY source_name, source_url, data_status
ORDER BY records DESC;

-- Duplicate rows by location and year
SELECT
    location_name,
    year,
    COUNT(*) AS row_count
FROM staging.stg_jma_sakura
GROUP BY location_name, year
HAVING COUNT(*) > 1
ORDER BY row_count DESC, location_name, year
LIMIT 20;