import re
import time
from typing import List, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import text

from src.db.db import get_engine

BASE_URL = "https://www.data.jma.go.jp/stats/etrn/view/monthly_s3_en.php"
STATION_LIST_URL = "https://www.data.jma.go.jp/stats/data/en/smp/index.html"

TEMP_VIEW = 1
PRECIP_VIEW = 13
BAD_STATION_CODES = {
    "47429",  # MORI
    "47627",  # TSUKUBASAN
    "47650",  # KAMEYAMA
    "47676",  # NIIJIKA
    "47751",  # IBUKIYAMA
    "47763",  # HOUFU
    "47894",  # TSURUGISAN
    "47963",  # TORISHIMA
    "47673", # TOMISAKI
}

def get_station_list() -> List[Tuple[str, str]]:
    """
    Scrape station names and station codes from the JMA monthly statistics page.
    Returns a list of (station_name, station_code).
    """
    resp = requests.get(STATION_LIST_URL, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    station_select = soup.find("select", {"name": "block_no"})
    if station_select is None:
        raise ValueError("Could not find station <select name='block_no'> on JMA page.")

    stations: List[Tuple[str, str]] = []

    for option in station_select.find_all("option"):
        station_code = option.get("value", "").strip()
        text_value = option.get_text(" ", strip=True)

        if not station_code:
            continue

        if station_code in BAD_STATION_CODES:
            continue

        # Remove the WMO / Station No suffix from the visible label
        station_name = re.split(r"WMO Station ID:|Station No:", text_value)[0]
        station_name = station_name.replace("\xa0", " ")
        station_name = re.sub(r"\s+", " ", station_name).strip()

        # Normalize weird spaces
        station_name = station_name.replace("\xa0", " ").strip()

        if "(OLD)" in station_name:
            continue

        if station_name:
            stations.append((station_name, station_code))

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for station_name, station_code in stations:
        key = (station_name, station_code)
        if key not in seen:
            seen.add(key)
            deduped.append(key)

    if not deduped:
        raise ValueError("No stations found on JMA station list page.")

    return deduped


def build_url(station_code: str, view: int) -> str:
    return f"{BASE_URL}?block_no={station_code}&view={view}"


def extract_table(url: str) -> pd.DataFrame:
    tables = pd.read_html(url, flavor="lxml")
    if len(tables) < 2:
        raise ValueError(f"Expected at least 2 tables at {url}, got {len(tables)}")
    return tables[1].copy()


def transform_monthly_table(df: pd.DataFrame, value_name: str) -> pd.DataFrame:
    month_cols = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    missing = [c for c in ["Year"] + month_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns {missing}. Got columns: {list(df.columns)}")

    df = df[["Year"] + month_cols].copy()

    df_long = df.melt(
        id_vars="Year",
        value_vars=month_cols,
        var_name="month_name",
        value_name=value_name
    )

    month_map = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    # Clean JMA annotations like " ]" or ")" and blank full-width spaces
    df_long["year"] = pd.to_numeric(df_long["Year"], errors="coerce")
    df_long["month"] = df_long["month_name"].map(month_map)

    cleaned = (
        df_long[value_name]
        .astype(str)
        .str.replace("\u3000", "", regex=False)   # full-width space
        .str.replace(r"[^0-9.\-]", "", regex=True)
        .replace("", pd.NA)
    )

    df_long[value_name] = pd.to_numeric(cleaned, errors="coerce")

    df_long = df_long.dropna(subset=["year", "month"])
    df_long["year"] = df_long["year"].astype(int)
    df_long["month"] = df_long["month"].astype(int)

    return df_long[["year", "month", value_name]].copy()


def fetch_station_data(station_name: str, station_code: str) -> pd.DataFrame:
    temp_url = build_url(station_code, TEMP_VIEW)
    precip_url = build_url(station_code, PRECIP_VIEW)

    temp_raw = extract_table(temp_url)
    precip_raw = extract_table(precip_url)

    temp_long = transform_monthly_table(temp_raw, "mean_temp_c")
    precip_long = transform_monthly_table(precip_raw, "precipitation_mm")

    final_df = temp_long.merge(
        precip_long,
        on=["year", "month"],
        how="outer"
    )

    final_df["station_name"] = station_name
    final_df["station_code"] = station_code
    final_df["source_url"] = temp_url

    final_df = final_df[
        [
            "source_url",
            "station_name",
            "station_code",
            "year",
            "month",
            "mean_temp_c",
            "precipitation_mm",
        ]
    ].copy()

    return final_df


def load_raw(df: pd.DataFrame, engine) -> None:
    with engine.begin() as conn:
        # Replace the whole raw table content for a clean reload
        conn.execute(text("TRUNCATE TABLE raw.jma_monthly_climate"))

    df.to_sql(
        "jma_monthly_climate",
        engine,
        schema="raw",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )


def main():
    engine = get_engine()

    stations = get_station_list()
    print(f"Stations found: {len(stations)}")

    all_frames = []
    failed = []

    for i, (station_name, station_code) in enumerate(stations, start=1):
        try:
            print(f"[{i}/{len(stations)}] Fetching {station_name} ({station_code})")
            station_df = fetch_station_data(station_name, station_code)
            all_frames.append(station_df)
            time.sleep(0.2)  # polite delay
        except Exception as e:
            print(f"Failed for {station_name} ({station_code}): {e}")
            failed.append((station_name, station_code, str(e)))

    if not all_frames:
        raise ValueError("No station data was fetched successfully.")

    final_df = pd.concat(all_frames, ignore_index=True)

    print("\n--- FINAL DATAFRAME PREVIEW ---")
    print(final_df.head(20))
    print(f"Rows to load: {len(final_df)}")
    print(f"Failed stations: {len(failed)}")

    load_raw(final_df, engine)
    print("Load completed into raw.jma_monthly_climate")

    if failed:
        print("\n--- FAILED STATIONS ---")
        for item in failed[:20]:
            print(item)


if __name__ == "__main__":
    main()