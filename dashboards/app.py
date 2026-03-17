# Imports & path setup
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import streamlit as st
import pandas as pd
import plotly.express as px
from src.db.db import get_engine

# Import dashboard query functions
from src.viz.dashboard_queries import (
    get_station_list,
    get_climate_timeseries,
    get_climate_kpis,
)

# Page configuration
st.set_page_config(page_title="Seasonal Japan", page_icon="🌸", layout="wide")

# Function for consistent chart styling
def style_fig(fig):
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified", # Show all values for given x-position
        title_x=0.05, # Slightly align title to the left
        margin=dict(l=40, r=40, t=60, b=40), # Increase spacing for minimal layout
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Helvetica, Arial, sans-serif", size=12, color="#5B4D53")
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_traces(line=dict(color="#E8AFCF", width=2), selector=dict(type="scatter"))
    return fig

# App title & description
st.title("Seasonal Japan 🌸")
st.markdown("Explore long-term monthly climate patterns across Japan, including temperature, precipitation, and seasonal variation by weather station.")

# Station selector
stations = get_station_list()

station_label_map = {
    row["station_name"]: row["station_code"]
    for _, row in stations.iterrows()
}

selected_name = st.selectbox(
    "Please choose a station ▼",
    options=list(station_label_map.keys())
)

selected_station_code = station_label_map[selected_name]

# Load time series and KPIs for selected station
df = get_climate_timeseries(selected_station_code)
kpi_df = get_climate_kpis(selected_station_code)

# Aggregate to yearly level
df["date_key"] = pd.to_datetime(df["date_key"])
df["year"] = df["date_key"].dt.year
yearly_df = (
    df.groupby("year", as_index=False)
    .agg({"mean_temp_c": "mean", "precipitation_mm": "sum"})
)

# Handle case where no data is found for the station
if df.empty:
    st.warning("No data found for this station.")
    st.stop()

# Extract station metadata
station_name = df["station_name"].dropna().iloc[0]
min_date = pd.to_datetime(df["date_key"]).min()
max_date = pd.to_datetime(df["date_key"]).max()

# Station title
st.subheader(f"Station • {station_name}")
st.caption(f"Data spans from {min_date.strftime('%b %Y')} to {max_date.strftime('%b %Y')}.")

# KPIs
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Years", int(kpi_df.loc[0, "total_years"]))
col2.metric("Average temperature (°C)", kpi_df.loc[0, "avg_temp_c"])
col3.metric("Average precipitation (mm)", kpi_df.loc[0, "avg_precipitation_mm"])
col4.metric("Minimum temperature (°C)", kpi_df.loc[0, "min_temp_c"])
col5.metric("Maximum temperature (°C)", kpi_df.loc[0, "max_temp_c"])

# Yearly temperature over time
temp_fig = px.line(
    yearly_df,
    x="year",
    y="mean_temp_c",
    title=f"🌡️ Yearly Temperature • {station_name}",
    labels={
        "year": "Year",
        "mean_temp_c": "Average temperature (°C)"
    }
)
temp_fig = style_fig(temp_fig)

# Yearly precipitation over time
precip_fig = px.line(
    yearly_df,
    x="year",
    y="precipitation_mm",
    title=f"🌧️ Yearly Precipitation • {station_name}",
    labels={
        "year": "Year",
        "precipitation_mm": "Precipitation (mm)"
    }
)
precip_fig = style_fig(precip_fig)

# Average temperature by season
seasonal_avg = (
    df.groupby("season", as_index=False)[["mean_temp_c", "precipitation_mm"]]
    .mean()
)

# Map season names to emojis
season_map = {
    "spring": "🌷",
    "summer": "☀️",
    "fall": "🍂",
    "winter": "🌨️"
}
seasonal_avg["season"] = seasonal_avg["season"].map(season_map)

# Assign custom colours to seasons
season_colors = {
    "🌷": "#DE52AF",  # Tulip pink
    "☀️": "#ECB633",  # Sun yellow
    "🍂": "#E0773B",    # Maple orange
    "🌨️": "#C7C3FF"   # Snowy purple
}

# Assign chronological season order
season_order = ["🌷", "☀️", "🍂", "🌨️"]
seasonal_avg["season"] = pd.Categorical(
    seasonal_avg["season"],
    categories=season_order,
    ordered=True
)
seasonal_avg = seasonal_avg.sort_values("season")

# Seasonal average temperature chart
season_temp_fig = px.bar(
    seasonal_avg,
    x="season",
    y="mean_temp_c",
    color="season",
    title=f"Average Temperature by Season • {station_name}",
    labels={
        "season": "Season",
        "mean_temp_c": "Average temperature (°C)"
    },
    color_discrete_map=season_colors
)
season_temp_fig.update_layout(showlegend=False)
season_temp_fig = style_fig(season_temp_fig)

# Display charts
st.plotly_chart(temp_fig, width='stretch')
st.plotly_chart(precip_fig, width='stretch')
st.plotly_chart(season_temp_fig, width='stretch')

# Optional: raw data table
# with st.expander("Show raw data"):
#    st.dataframe(df, width='stretch')

# Source footer
st.markdown("---")
st.caption(
    "Source: Japan Meteorological Agency (JMA) • Data updated as of March 2026"
)

# Run with: 
# streamlit run dashboards/app.py