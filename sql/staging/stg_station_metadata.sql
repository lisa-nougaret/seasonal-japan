DROP TABLE IF EXISTS staging.stg_station_metadata;

CREATE TABLE staging.stg_station_metadata (
    station_code TEXT PRIMARY KEY,
    station_name TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    source_url TEXT,
    metadata_ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);