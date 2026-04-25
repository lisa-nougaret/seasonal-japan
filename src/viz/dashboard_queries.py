import pandas as pd
from sqlalchemy import text
from src.db.db import get_engine

def get_station_list() -> pd.DataFrame:
    query = """
    SELECT
        station_code,
        location_code,
        station_name,
        latitude,
        longitude
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
        prediction_status,
        is_best_model,
        trained_at
    FROM analytics.fact_sakura_forecast
    WHERE location_code = :location_code
      AND forecast_year = :year
      AND event_type = 'sakura_bloom'
      AND is_best_model = TRUE
    LIMIT 1;
    """)
    engine = get_engine()
    return pd.read_sql(
        query,
        engine,
        params={"location_code": location_code, "year": year},
    )

def get_sakura_forecast_map(year: int = 2026) -> pd.DataFrame:
    query = text("""
        SELECT
            s.station_code,
            s.location_code,
            s.station_name,
            s.latitude,
            s.longitude,
            f.forecast_year,
            f.predicted_day_of_year,
            f.predicted_event_date,
            f.model_name,
            f.mae_days,
            f.rmse_days
        FROM analytics.fact_sakura_forecast f
        JOIN analytics.dim_station s
            ON f.location_code::text = s.location_code::text
        WHERE f.forecast_year = :year
            AND f.event_type = 'sakura_bloom'
            AND f.is_best_model = TRUE
            AND s.latitude IS NOT NULL
            AND s.longitude IS NOT NULL
        ORDER BY f.predicted_event_date
    """)

    engine = get_engine()

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"year": year})

    if not df.empty:
        df['predicted_event_date'] = pd.to_datetime(df['predicted_event_date'])
        df['bloom_label'] = df['predicted_event_date'].dt.strftime('%d %b %Y')
        df['mae_days'] = pd.to_numeric(df['mae_days'], errors='coerce')
        df['rmse_days'] = pd.to_numeric(df['rmse_days'], errors='coerce')
        df["predicted_day_of_year"] = pd.to_numeric(df["predicted_day_of_year"], errors='coerce')

    return df