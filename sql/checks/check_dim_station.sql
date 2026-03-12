SELECT *
FROM analytics.dim_station
ORDER BY station_code
LIMIT 20;
SELECT COUNT(*)
FROM analytics.dim_station;