import pandas as pd
from sqlalchemy import text
from src.db.db import get_engine

def get_station_list() -> pd.DataFrame:
    query = """
    SELECT
        station_code,
        station_name
    FROM analytics.dim_station
    ORDER BY station_name;
    """
    engine = get_engine()
    return pd.read_sql(query, engine)

def get_climate_timeseries(station_code: str) -> pd.DataFrame:
    query = text("""
    SELECT
        f.station_code,
        s.station_name,
        m.date_key,
        f.mean_temp_c,
        f.precipitation_mm,
        m.season
    FROM analytics.fact_monthly_climate f
    LEFT JOIN analytics.dim_station s
        ON f.station_code = s.station_code
    LEFT JOIN analytics.dim_month m
        ON f.date_key = m.date_key
    WHERE f.station_code = :station_code
    ORDER BY m.date_key;
    """)
    engine = get_engine()
    return pd.read_sql(query, engine, params={"station_code": station_code})

def get_climate_kpis(station_code: str) -> pd.DataFrame:
    query = text("""
    SELECT
        COUNT(*) AS total_months,
        COUNT(*) / 12 AS total_years,
        ROUND(AVG(mean_temp_c)::numeric, 2) AS avg_temp_c,
        ROUND(AVG(precipitation_mm)::numeric, 2) AS avg_precipitation_mm,
        ROUND(MIN(mean_temp_c)::numeric, 2) AS min_temp_c,
        ROUND(MAX(mean_temp_c)::numeric, 2) AS max_temp_c
    FROM analytics.fact_monthly_climate
    WHERE station_code = :station_code;
    """)
    engine = get_engine()
    return pd.read_sql(query, engine, params={"station_code": station_code})

def get_bloom_history(location_code: str) -> pd.DataFrame:
    query = text("""
    SELECT
        location_code,
        year,
        date_key,
        day_of_year,
        event_type,
        data_status,
        source_name
    FROM analytics.fact_sakura_events
    WHERE location_code = :location_code
        AND event_type = 'sakura_bloom'
    ORDER BY year;
    """)
    engine = get_engine()
    return pd.read_sql(query, engine, params={"location_code": location_code})

def get_bloom_temp_features(station_code: str, location_code: str) -> pd.DataFrame:
    query = text("""
    WITH bloom AS (
        SELECT
            location_code,
            year,
            date_key,
            day_of_year
        FROM analytics.fact_sakura_events
        WHERE location_code = :location_code
          AND event_type = 'sakura_bloom'
    ),
    late_winter_temp AS (
        SELECT
            f.station_code,
            EXTRACT(YEAR FROM f.date_key)::int AS year,
            ROUND(AVG(f.mean_temp_c)::numeric, 2) AS mean_temp_feb_mar
        FROM analytics.fact_monthly_climate f
        WHERE f.station_code = :station_code
          AND EXTRACT(MONTH FROM f.date_key) IN (2, 3)
        GROUP BY f.station_code, EXTRACT(YEAR FROM f.date_key)
    )
    SELECT
        b.year,
        b.date_key,
        b.day_of_year,
        t.mean_temp_feb_mar
    FROM bloom b
    LEFT JOIN late_winter_temp t
        ON b.year = t.year
    ORDER BY b.year;
    """)
    engine = get_engine()
    return pd.read_sql(
        query,
        engine,
        params={
            "station_code": station_code,
            "location_code": location_code
        }
    )

def get_bloom_forecast(location_code: str, year: int = 2026) -> pd.DataFrame:
    query = text("""
    SELECT
        location_code,
        forecast_year,
        predicted_day_of_year,
        predicted_event_date,
        model_name,
        model_version,
        prediction_status
    FROM analytics.fact_sakura_forecast
    WHERE location_code = :location_code
      AND forecast_year = :year
      AND event_type = 'sakura_bloom'
    ORDER BY
        CASE model_name
            WHEN 'random_forest' THEN 1
            WHEN 'hist_gradient_boosting' THEN 2
            WHEN 'linear_regression' THEN 3
            ELSE 99
        END,
        model_version DESC
    LIMIT 1;
    """)
    engine = get_engine()
    return pd.read_sql(
        query,
        engine,
        params={"location_code": location_code, "year": year}
    )