from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import DateTime, Numeric, String, text

from src.db.db import get_engine

BASE_URL = "https://www.data.jma.go.jp/stats/etrn/view/monthly_s3_en.php"

def parse_jma_coordinate(value: str) -> Optional[float]:
    """
    Converts JMA coordinates like: 35o39.2'N 136o03.7'E into decimal degrees.
    """
    if not value:
        return None

    value = (
        value.replace("°", "o")
        .replace("º", "o")
        .replace("’", "'")
        .replace("′", "'")
        .replace("\xa0", " ")
        .strip()
    )

    match = re.search(r"(\d+)\s*o\s*(\d+(?:\.\d+)?)'\s*([NSEW])", value)

    if not match:
        return None

    degrees = float(match.group(1))
    minutes = float(match.group(2))
    direction = match.group(3)

    decimal = degrees + minutes / 60

    if direction in {"S", "W"}:
        decimal *= -1

    return round(decimal, 6)

def build_url(station_code: str) -> str:
    return f"{BASE_URL}?block_no={station_code}&view=1"

def get_station_list_from_climate_table() -> list[tuple[str, str]]:
    query = """
        SELECT DISTINCT
            station_name,
            station_code
        FROM staging.stg_jma_monthly_climate
        WHERE station_code IS NOT NULL
          AND station_name IS NOT NULL
        ORDER BY station_code;
    """

    engine = get_engine()

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return list(df[["station_name", "station_code"]].itertuples(index=False, name=None))

def fetch_station_metadata(station_name: str, station_code: str) -> dict:
    station_code = str(station_code)
    url = build_url(station_code)

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    caption = soup.find("caption", {"class": "m"})

    if caption is None:
        print(f"Could not find caption for {station_name} ({station_code})")
        return {
            "station_code": station_code,
            "station_name": station_name,
            "latitude": None,
            "longitude": None,
            "source_url": url,
            "metadata_ingested_at": datetime.now(),
        }

    caption_text = caption.get_text(" ", strip=True)
    caption_text = caption_text.replace("\xa0", " ")
    caption_text = re.sub(r"\s+", " ", caption_text)

    lat_match = re.search(
        r"Lat\s+(\d+\s*o\s*\d+(?:\.\d+)?'\s*[NS])",
        caption_text,
    )

    lon_match = re.search(
        r"Lon\s+(\d+\s*o\s*\d+(?:\.\d+)?'\s*[EW])",
        caption_text,
    )

    latitude = parse_jma_coordinate(lat_match.group(1)) if lat_match else None
    longitude = parse_jma_coordinate(lon_match.group(1)) if lon_match else None

    if latitude is None or longitude is None:
        print(f"Could not parse coordinates for {station_name} ({station_code})")
        print(f"Caption text: {caption_text}")

    return {
        "station_code": station_code,
        "station_name": station_name,
        "latitude": latitude,
        "longitude": longitude,
        "source_url": url,
        "metadata_ingested_at": datetime.now(),
    }

def load_station_metadata() -> None:
    stations = get_station_list_from_climate_table()

    print(f"Stations to enrich: {len(stations)}")

    rows = []
    failed = []

    for i, (station_name, station_code) in enumerate(stations, start=1):
        try:
            print(f"[{i}/{len(stations)}] Fetching metadata for {station_name} ({station_code})")
            rows.append(fetch_station_metadata(station_name, station_code))
            time.sleep(0.2)
        except Exception as e:
            print(f"Failed for {station_name} ({station_code}): {e}")
            failed.append((station_name, station_code, str(e)))

    df = pd.DataFrame(rows)

    if df.empty:
        raise ValueError("No station metadata extracted.")

    df["station_code"] = df["station_code"].astype(str)
    df["station_name"] = df["station_name"].astype("string")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["source_url"] = df["source_url"].astype("string")

    print("\n▼ STATION METADATA PREVIEW ▼")
    print(df.head(20))
    print(f"Rows extracted: {len(df)}")
    print(f"Missing latitude: {df['latitude'].isna().sum()}")
    print(f"Missing longitude: {df['longitude'].isna().sum()}")
    print(f"Failed stations: {len(failed)}")

    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM staging.stg_station_metadata;"))

    df.to_sql(
        "stg_station_metadata",
        engine,
        schema="staging",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
        dtype={
            "station_code": String(),
            "station_name": String(),
            "latitude": Numeric(),
            "longitude": Numeric(),
            "source_url": String(),
            "metadata_ingested_at": DateTime(),
        },
    )

    print("Load has been completed into staging.stg_station_metadata.")

    if failed:
        print("\n▼ FAILED STATIONS ▼")
        for item in failed[:20]:
            print(item)

if __name__ == "__main__":
    load_station_metadata()