from __future__ import annotations 

# Import necessary libraries and modules
import re
from datetime import datetime
from io import StringIO
from typing import Optional
from numpy import rint
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import table, text
from src.db.db import get_engine

# Constants for JMA sakura bloom data
SOURCE_NAME = "jma_sakura" # Name of the data source for JMA sakura bloom data
FIRST_BLOOM_URL = "https://www.data.jma.go.jp/sakura/data/ruinenchi/004.csv" # URL for sakura bloom data from JMA
FULL_BLOOM_URL = "https://www.data.jma.go.jp/sakura/data/ruinenchi/005.csv" # URL for full bloom data from JMA (note to myself: not currently used in this script, but can be added in the future if needed)
RAW_TABLE = "jma_sakura_raw" # Name of the raw data table in the database
RAW_SCHEMA = "raw" # Name of the database schema for raw data
EVENT_TYPE = "sakura_bloom" # Type of event being recorded
DATA_STATUS = "observed" # Status of the data being recorded

# Regular expression pattern to extract year and bloom date from the data
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

TIMEOUT_SECONDS = 20


# Functions

# Function to fetch text content from a given URL
def fetch_text(url: str) -> str:
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=TIMEOUT_SECONDS)
    response.raise_for_status() # Raise an exception if the request was unsuccessful
    response.encoding = response.apparent_encoding or "utf-8" # Set the correct encoding for the response
    return response.text

# Function to parse JMA CSV data
def parse_jma_csv(csv_text: str) -> pd.DataFrame:
    df = pd.read_csv(StringIO(csv_text)) # Read the CSV text into a DataFrame without assuming any header row
    return df

# Function to clean text values by stripping whitespace and converting certain values to None
def clean_text(value) -> Optional[str]:
    if pd.isna(value):
        return None
    value = str(value).strip()
    if value in {"", "-", "—", "－", "―", "nan", "None"}:
        return None
    return value

# Function to extract a 4-digit year from a column name using a regular expression (e.g., "2026年" or "Year 2026")
def extract_year_from_column(col_name: str) -> Optional[int]:
    match = re.search(r"(19|20)\d{2}", col_name)
    if match:
        return int(match.group(0))
    return None

# Function to identify year value columns
def extract_year_value_columns(df: pd.DataFrame) -> list[str]:
    cols = []
    for col in df.columns:
        col_s = str(col).strip()
        if re.fullmatch(r"(19|20)\d{2}", col_s):
            cols.append(col)
    return cols

# Function to identify year attribute columns such as "1953rm", "1954rm", etc.
def extract_year_rm_columns(df: pd.DataFrame) -> dict[int, str]:
    rm_cols = {}
    for col in df.columns:
        col_s = str(col).strip().lower().replace(" ", "")
        match = re.fullmatch(r"((19|20)\d{2})rm", col_s)
        if match:
            rm_cols[int(match.group(1))] = col
    return rm_cols

# Function to normalize raw event date values by keeping them as text in the raw layer and converting certain values to None (e.g., '3/26' -> '3/26', 'Mar 26' -> 'Mar 26', '-' -> None)
def normalize_event_date_raw(value) -> Optional[str]:
    value = clean_text(value)
    if value is None:
        return None
    
    s = str(value).strip()

    # Convert JMA MMDD-style numeric values such as 326 -> 03-26 or 402 -> 04-02
    if re.fullmatch(r"\d{3,4}", s):
        n = int(s)
        month = n // 100
        day = n % 100
        if 1 <= month <= 12 and 1 <= day <= 31:
            return f"{month:02d}-{day:02d}"

    return s

# Function to detect and rename metadata columns from the JMA CSV
def rename_metadata_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    rename_map = {}
    for col in df.columns:
        col_s = str(col).strip()

        # Station name column
        if col_s in {"地点名", "地点"}:
            rename_map[col] = "location_name_raw"

        # Station code column
        elif col_s in {"番号", "地点番号"}:
            rename_map[col] = "station_code_raw"

    df = df.rename(columns=rename_map)
    return df


# Function to reshape a wide historical JMA sakura CSV into long format, where one row represents one location and one year
def reshape_jma_ruinenchi_to_long(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = rename_metadata_columns(df)

    if "location_name_raw" not in df.columns:
        # Fallback: assume the first column is the location column if the expected Japanese label is not present
        first_col = df.columns[0]
        df = df.rename(columns={first_col: "location_name_raw"})

    year_cols = extract_year_value_columns(df)
    if not year_cols:
        raise ValueError(
            "Could not identify any year value columns in JMA sakura CSV. "
            "Inspect the CSV structure and adjust parsing."
        )

    id_vars = [col for col in ["station_code_raw", "location_name_raw"] if col in df.columns]

    long_df = df.melt(
        id_vars=id_vars,
        value_vars=year_cols,
        var_name="year_col",
        value_name="event_date_raw",
    )

    long_df["year"] = long_df["year_col"].apply(lambda col: extract_year_from_column(str(col)))
    long_df["event_date_raw"] = long_df["event_date_raw"].apply(normalize_event_date_raw)
    long_df["location_name_raw"] = long_df["location_name_raw"].apply(clean_text)

    if "station_code_raw" in long_df.columns:
        long_df["station_code_raw"] = long_df["station_code_raw"].apply(clean_text)

    long_df = long_df.drop(columns=["year_col"])
    long_df = long_df.dropna(subset=["location_name_raw", "year"], how="any")  # Drop rows where either 'location_name_raw' or 'year' is missing, as both are essential for the analysis

    # Attach RM attribute columns if they exist in the source CSV
    rm_cols = extract_year_rm_columns(df)
    if rm_cols:
        rm_frames = []

        for year, rm_col in rm_cols.items():
            rm_df = df[id_vars + [rm_col]].copy()
            rm_df["year"] = year
            rm_df = rm_df.rename(columns={rm_col: "rm_raw"})
            rm_frames.append(rm_df)

        rm_long_df = pd.concat(rm_frames, ignore_index=True)
        if "rm_raw" in rm_long_df.columns:
            rm_long_df["rm_raw"] = rm_long_df["rm_raw"].apply(clean_text)

        join_keys = [col for col in ["station_code_raw", "location_name_raw", "year"] if col in long_df.columns and col in rm_long_df.columns]
        long_df = long_df.merge(rm_long_df, on=join_keys, how="left")

    return long_df


# Function to build the final raw DataFrame for ingestion by parsing the CSV, reshaping it to long format, and adding metadata columns
def build_raw_dataframe(csv_text: str) -> pd.DataFrame:
    table = parse_jma_csv(csv_text)

    # Debug: print the first few rows and columns of the extracted table to verify that it was parsed correctly before reshaping
    # print(table.head())
    # print(table.columns.tolist())

    long_df = reshape_jma_ruinenchi_to_long(table)

    raw_ingested_at = pd.Timestamp.utcnow()
    page_notes = "JMA ruinenchi CSV"

    long_df["event_type"] = EVENT_TYPE
    long_df["data_status"] = DATA_STATUS
    long_df["source_name"] = SOURCE_NAME
    long_df["source_url"] = FIRST_BLOOM_URL
    long_df["page_notes"] = page_notes
    long_df["raw_ingested_at"] = raw_ingested_at

    # Reorder columns
    ordered_columns = [
        "raw_ingested_at",
        "source_name",
        "source_url",
    ]

    if "station_code_raw" in long_df.columns:
        ordered_columns.append("station_code_raw")

    ordered_columns.extend(
        [
            "location_name_raw",
            "year",
        ]
    )

    if "rm_raw" in long_df.columns:
        ordered_columns.append("rm_raw")

    ordered_columns.extend(
        [
            "event_type",
            "event_date_raw",
            "data_status",
            "page_notes",
        ]
    )

    long_df = long_df[ordered_columns]

    return long_df


# Below are functions related to database operations, such as creating the raw table if it does not exist, deleting existing rows for this source before reload, and loading the new data into the raw table.

# Function to create the raw table in the database if it does not already exist, with the appropriate schema for the JMA sakura bloom data
def create_raw_table_if_not_exists() -> None:
    """
    Create the raw table in the database for JMA sakura bloom data if it does not already exist.
    """
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {RAW_SCHEMA}.{RAW_TABLE} (
        raw_ingested_at TIMESTAMP,
        source_name TEXT,
        source_url TEXT,
        station_code_raw TEXT,
        location_name_raw TEXT,
        year INTEGER,
        rm_raw TEXT,
        event_type TEXT,
        event_date_raw TEXT,
        data_status TEXT,
        page_notes TEXT
    );
    """

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(create_sql))


# Function to delete existing rows in the raw table for this specific source, event type, and data status before loading new data, to ensure a clean reload
def delete_existing_sakura_rows_for_source() -> None:
    delete_sql = f"""
    DELETE FROM {RAW_SCHEMA}.{RAW_TABLE}
    WHERE source_name = :source_name
      AND event_type = :event_type
      AND data_status = :data_status
    """

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(delete_sql),
            {
                "source_name": SOURCE_NAME,
                "event_type": EVENT_TYPE,
                "data_status": DATA_STATUS,
            },
        )


# Function to load the prepared DataFrame into the raw table in the database using SQLAlchemy's to_sql method
def load_to_raw(df: pd.DataFrame) -> None:
    engine = get_engine()
    df.to_sql(
        name=RAW_TABLE,
        con=engine,
        schema=RAW_SCHEMA,
        if_exists="append",
        index=False,
        method="multi",
    )


# Function to orchestrate the entire data ingestion process for JMA sakura bloom data, including fetching the CSV, building the raw DataFrame, ensuring the raw table exists, deleting existing rows for this source, and loading the new data into the raw table.
def main() -> None:
    print("Fetching sakura source CSV...")
    csv_text = fetch_text(FIRST_BLOOM_URL)

    print("Parsing sakura CSV...")
    df_raw = build_raw_dataframe(csv_text)

    print(f"Rows prepared: {len(df_raw)}")
    print(df_raw.head(10))

    print("Ensuring raw table exists...")
    create_raw_table_if_not_exists()

    print("Deleting previous source rows...")
    delete_existing_sakura_rows_for_source()

    print("Loading into raw.jma_sakura_raw ...")
    load_to_raw(df_raw)

    print("Done.")


if __name__ == "__main__":
    main()