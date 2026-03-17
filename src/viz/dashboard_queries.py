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
        d.date_key,
        d.year,
        d.month,
        d.quarter,
        d.season,
        f.mean_temp_c,
        f.precipitation_mm
    FROM analytics.fact_monthly_climate f
    LEFT JOIN analytics.dim_station s
        ON f.station_code = s.station_code
    LEFT JOIN analytics.dim_date d
        ON f.date_key = d.date_key
    WHERE f.station_code = :station_code
    ORDER BY d.date_key;
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