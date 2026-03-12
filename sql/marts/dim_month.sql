DROP TABLE IF EXISTS analytics.dim_month;
CREATE TABLE analytics.dim_month AS
SELECT DISTINCT month_start_date AS date_key,
    year,
    month,
    EXTRACT(
        QUARTER
        FROM month_start_date
    ) AS quarter,
    CASE
        WHEN month IN (12, 1, 2) THEN 'winter'
        WHEN month IN (3, 4, 5) THEN 'spring'
        WHEN month IN (6, 7, 8) THEN 'summer'
        WHEN month IN (9, 10, 11) THEN 'fall'
    END AS season
FROM staging.stg_jma_monthly_climate
ORDER BY date_key;