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
st.markdown("""
<div class="hero-block">
    <h1 style="font-weight: 300;">When Will Sakura Bloom This Year?</h1>
    <p style="font-weight: 300;">
        Explore historical temperature patterns and forecasted sakura first bloom dates, across Japan.
    </p>
</div>
""", unsafe_allow_html=True)

# Load stations
stations = get_station_list()

station_label_map = {
    row["station_name"]: row["station_code"]
    for _, row in stations.iterrows()
}

# Top filters
filter_col1, filter_col2, empty_col1, empty_col2 = st.columns([1, 1, 1, 1]) # the 2 columns on the right remain blank

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

# Prepare forecast values
if not forecast_df.empty and pd.notna(forecast_df.loc[0, "predicted_event_date"]):
    bloom_date = pd.to_datetime(forecast_df.loc[0, "predicted_event_date"]).strftime("%d %b %Y")
    bloom_doy = int(forecast_df.loc[0, "predicted_day_of_year"])
    model_name = forecast_df.loc[0, "model_name"]
    model_version = forecast_df.loc[0, "model_version"]
else:
    bloom_date = "Not available"
    bloom_doy = "—"
    model_name = "Not available"
    model_version = ""

model_label_map = {
    "linear_regression": "Linear Regression",
}

# KPI row
col1, col2, col3, empty_kpi = st.columns(4)
col1.metric("Forecasted bloom date", bloom_date)
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
    f"Source: Japan Meteorological Agency (JMA) • Forecast model — {model_label_map.get(model_name)} • Updated March 2026"
)