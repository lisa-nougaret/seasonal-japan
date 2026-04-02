-- Check the total number of records in the fact table
SELECT COUNT(*) AS total_rows
FROM analytics.fact_monthly_climate;

-- Check the date coverage
SELECT
    MIN(date_key) AS first_month,
    MAX(date_key) AS last_month
FROM analytics.fact_monthly_climate;

-- Check the distribution of records by station
SELECT
    f.station_code,
    s.station_name,
    COUNT(*) AS records
FROM analytics.fact_monthly_climate f
LEFT JOIN analytics.dim_station s
    ON f.station_code = s.station_code
GROUP BY f.station_code, s.station_name
ORDER BY records DESC;

-- Check for null values in measures
SELECT
    COUNT(*) AS total_rows,
    COUNT(mean_temp_c) AS non_null_temperature,
    COUNT(precipitation_mm) AS non_null_precipitation
FROM analytics.fact_monthly_climate;

-- Check for duplicate records based on station_code + date_key
SELECT
    station_code,
    date_key,
    COUNT(*) AS duplicate_count
FROM analytics.fact_monthly_climate
GROUP BY station_code, date_key
HAVING COUNT(*) > 1;

-- Check the range of mean_temp_c
SELECT
    MIN(mean_temp_c) AS min_temp,
    MAX(mean_temp_c) AS max_temp
FROM analytics.fact_monthly_climate;

-- Check the range of precipitation_mm
SELECT
    MIN(precipitation_mm) AS min_precipitation,
    MAX(precipitation_mm) AS max_precipitation
FROM analytics.fact_monthly_climate;

-- Check the distribution of records by season
SELECT
    d.season,
    COUNT(*) AS records
FROM analytics.fact_monthly_climate f
LEFT JOIN analytics.dim_date d
    ON f.date_key = d.date_key
GROUP BY d.season
ORDER BY d.season;

-- Check the distribution of records by quarter
SELECT
    d.quarter,
    COUNT(*) AS records
FROM analytics.fact_monthly_climate f
LEFT JOIN analytics.dim_date d
    ON f.date_key = d.date_key
GROUP BY d.quarter
ORDER BY d.quarter;

-- Check average temperature by season
SELECT
    d.season,
    ROUND(AVG(f.mean_temp_c), 2) AS avg_temp
FROM analytics.fact_monthly_climate f
LEFT JOIN analytics.dim_date d
    ON f.date_key = d.date_key
GROUP BY d.season
ORDER BY avg_temp;