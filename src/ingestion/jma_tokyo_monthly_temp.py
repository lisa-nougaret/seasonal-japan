import pandas as pd
from sqlalchemy import text
from src.db import get_engine

STATION_NAME = "TOKYO"
STATION_CODE = "47662"
SOURCE_URL = (
    "https://www.data.jma.go.jp/stats/etrn/view/monthly_s3_en.php"
    "?block_no=47662&view=1"
)

engine = get_engine()


def extract_table(url: str) -> pd.DataFrame:
    tables = pd.read_html(url, flavor="lxml")
    if len(tables) < 2:
        raise ValueError("Expected at least 2 tables on JMA page")
    return tables[1].copy()


def transform_table(df: pd.DataFrame) -> pd.DataFrame:
    # Keep only monthly columns
    month_cols = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    df = df[["Year"] + month_cols].copy()

    # Convert from wide format to long format
    df_long = df.melt(
        id_vars="Year",
        value_vars=month_cols,
        var_name="month_name",
        value_name="mean_temp_c"
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

    df_long["year"] = pd.to_numeric(df_long["Year"], errors="coerce")
    df_long["month"] = df_long["month_name"].map(month_map)
    df_long["mean_temp_c"] = pd.to_numeric(df_long["mean_temp_c"], errors="coerce")

    df_long = df_long.dropna(subset=["mean_temp_c"])

    df_long["year"] = df_long["year"].astype(int)
    df_long["month"] = df_long["month"].astype(int)

    df_long["source_url"] = SOURCE_URL
    df_long["station_name"] = STATION_NAME
    df_long["station_code"] = STATION_CODE

    final_df = df_long[
        [
            "source_url",
            "station_name",
            "station_code",
            "year",
            "month",
            "mean_temp_c",
        ]
    ].copy()

    return final_df


def load_raw(df: pd.DataFrame) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                DELETE FROM raw.jma_monthly_climate
                WHERE station_code = :station_code
                """
            ),
            {"station_code": STATION_CODE},
        )

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
    raw_df = extract_table(SOURCE_URL)
    final_df = transform_table(raw_df)

    print(final_df.head(12))
    print(f"Rows to load: {len(final_df)}")

    load_raw(final_df)
    print("Load completed into raw.jma_monthly_climate")


if __name__ == "__main__":
    main()