DROP IS TABLE IF EXISTS analytics.dim_date;
CREATE TABLE analytics.dim_date AS
SELECT DISTINCT
    event_date AS date_key,
    EXTRACT(YEAR FROM event_date) AS year,
    EXTRACT(MONTH FROM event_date) AS month,
    EXTRACT(DAY FROM event_date) AS day,
    EXTRACT(DOY FROM event_date) AS day_of_year,
    EXTRACT(QUARTER FROM event_date) AS quarter,
    CASE
        WHEN EXTRACT(MONTH FROM event_date) IN (3, 4, 5) THEN 'Spring'
        WHEN EXTRACT(MONTH FROM event_date) IN (6, 7, 8) THEN 'Summer'
        WHEN EXTRACT(MONTH FROM event_date) IN (9, 10, 11) THEN 'Autumn'
        ELSE 'Winter'
    END AS season
FROM staging.stg_jma_sakura;