DROP TABLE IF EXISTS analytics.fact_sakura_bloom_gap;

CREATE TABLE analytics.fact_sakura_bloom_gap AS
WITH first_bloom AS (
    SELECT
        location_code,
        year,
        day_of_year AS first_bloom_doy
    FROM analytics.fact_sakura_events
    WHERE event_type = 'sakura_bloom'
      AND day_of_year IS NOT NULL
),
full_bloom AS (
    SELECT
        location_code,
        year,
        day_of_year AS full_bloom_doy
    FROM analytics.fact_sakura_events
    WHERE event_type = 'sakura_fullbloom'
      AND day_of_year IS NOT NULL
),
paired AS (
    SELECT
        f.location_code,
        f.year,
        f.first_bloom_doy,
        fb.full_bloom_doy,
        fb.full_bloom_doy - f.first_bloom_doy AS gap_days
    FROM first_bloom f
    JOIN full_bloom fb
        ON  f.location_code = fb.location_code
        AND f.year          = fb.year
    WHERE fb.full_bloom_doy - f.first_bloom_doy BETWEEN 0 AND 30
)
SELECT
    location_code,
    ROUND(AVG(gap_days))::int AS avg_gap_days,
    COUNT(*)                  AS obs_count
FROM paired
GROUP BY location_code;
