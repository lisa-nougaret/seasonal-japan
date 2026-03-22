DROP TABLE IF EXISTS analytics.dim_location;
CREATE TABLE analytics.dim_location AS
SELECT
    location_code,
    location_name,
    MIN(year) AS first_year,
    MAX(year) AS last_year,
    COUNT(*) AS record_count
FROM staging.stg_jma_sakura
GROUP BY 
    location_code, 
    location_name;