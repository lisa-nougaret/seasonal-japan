-- Check total rows
SELECT
    COUNT(*) AS total_rows
FROM analytics.fact_sakura_training_features;

-- Check year range
SELECT
    MIN(year) AS min_year,
    MAX(year) AS max_year,
    COUNT(DISTINCT year) AS distinct_years
FROM analytics.fact_sakura_training_features;

-- Check distinct locations
SELECT
    COUNT(DISTINCT location_code) AS distinct_locations
FROM analytics.fact_sakura_training_features;

-- Null check
SELECT
    COUNT(*) AS total_rows,
    COUNT(day_of_year) AS non_null_day_of_year,
    COUNT(*) - COUNT(day_of_year) AS null_day_of_year
FROM analytics.fact_sakura_training_features;