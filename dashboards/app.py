# Run with streamlit run dashboards/app.py

# Imports & path setup
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.viz.dashboard_queries import (
    get_station_list,
    get_climate_timeseries,
    get_climate_kpis,
    get_bloom_forecast,
)

# Page configuration
st.set_page_config(page_title="Seasonal Japan", page_icon="🌸", layout="wide")

# Function for consistent chart styling
def style_fig(fig):
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        title_x=0.05,
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Helvetica, Arial, sans-serif",
            size=12,
            color="#5B4D53"
        )
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_traces(
        line=dict(color="#E8AFCF", width=2),
        selector=dict(type="scatter")
    )
    return fig

# App title & description
st.title("Seasonal Japan 🍡")
st.markdown(
    "Explore long-term temperature patterns across Japan, and view the forecasted cherry blossom first bloom date, by station."
)

# Load stations
stations = get_station_list()

station_label_map = {
    row["station_name"]: row["station_code"]
    for _, row in stations.iterrows()
}

# Top filters
filter_col1, filter_col2 = st.columns([2, 1])

with filter_col1:
    selected_name = st.selectbox(
        "Please choose a station ▼",
        options=list(station_label_map.keys())
    )

with filter_col2:
    selected_n_years = st.selectbox(
        "Display the last ... years ▼",
        options=[10, 20, 30, 50, 100],
        index=2
    )

selected_station_code = station_label_map[selected_name]
selected_location_code = str(int(selected_station_code) - 47000)

forecast_df = get_bloom_forecast(selected_location_code, year=2026)

# Load data
df = get_climate_timeseries(selected_station_code)
kpi_df = get_climate_kpis(selected_station_code)

# Handle no climate data
if df.empty:
    st.warning("No climate data found for this station.")
    st.stop()

# Prepare climate data
df["date_key"] = pd.to_datetime(df["date_key"])
df["year"] = df["date_key"].dt.year

yearly_df = (
    df.groupby("year", as_index=False)
    .agg({"mean_temp_c": "mean"})
)

# Filter to last n years
max_year = yearly_df["year"].max()
min_year_to_keep = max_year - selected_n_years + 1

yearly_df = yearly_df[yearly_df["year"] >= min_year_to_keep]

# Extract station metadata
station_name = df["station_name"].dropna().iloc[0]
min_date = df["date_key"].min()
max_date = df["date_key"].max()

# Station title
st.subheader(f"Station • {station_name}")
st.caption(
    f"Climate data spans from {min_date.strftime('%b %Y')} to {max_date.strftime('%b %Y')}."
)

# Forecast display
st.markdown("### 🌸 Forecasted first bloom date")

if not forecast_df.empty and pd.notna(forecast_df.loc[0, "predicted_event_date"]):
    bloom_date = pd.to_datetime(forecast_df.loc[0, "predicted_event_date"])
    st.metric("Predicted first bloom", bloom_date.strftime("%d %b %Y"))
else:
    st.info("No bloom forecast available for this station.")

# KPI row
col1, col2, col3 = st.columns(3)
col1.metric("Years available", int(kpi_df.loc[0, "total_years"]))
col2.metric("Average temperature (°C)", kpi_df.loc[0, "avg_temp_c"])
col3.metric("Temperature range (°C)", f"{kpi_df.loc[0, 'min_temp_c']} to {kpi_df.loc[0, 'max_temp_c']}")

# Temperature chart only
temp_fig = px.line(
    yearly_df,
    x="year",
    y="mean_temp_c",
    title=f"🌡️ Average Yearly Temperature • Last {selected_n_years} Years",
    labels={
        "year": "Year",
        "mean_temp_c": "Average temperature (°C)"
    }
)
temp_fig = style_fig(temp_fig)

st.plotly_chart(temp_fig, width="stretch")

# Source footer
st.markdown("---")
st.caption(
    "Source: Japan Meteorological Agency (JMA) • Climate history & sakura bloom forecasting dataset • Updated March 2026"
)