# Run with streamlit run dashboards/app.py

# Imports & path setup
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.express as px

import base64

from src.viz.dashboard_queries import (
    get_station_list,
    get_climate_timeseries,
    get_climate_kpis,
    get_bloom_forecast,
    get_bloom_history,
    get_bloom_temp_features
)

import base64

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: left center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Subtle overlay */
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba(247, 244, 242, 0.1);
            z-index: 0;
        }}

        /* Keep content above overlay */
        .stApp > div {{
            position: relative;
            z-index: 1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def add_floating_petals(image_path: str):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .petal-overlay {{
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 9999;
            overflow: hidden;
        }}

        .petal {{
            position: absolute;
            width: 25px;
            opacity: 1;
            animation-name: fallDrift;
            animation-timing-function: linear;
            animation-iteration-count: infinite;
        }}

        .petal img {{
            width: 100%;
            display: block;
        }}

        /* Bigger delays = fewer petals at once */
        .petal-1 {{ left: 15%; top: -10%; animation-duration: 28s; animation-delay: 0s; }}
        .petal-2 {{ left: 55%; top: -15%; animation-duration: 30s; animation-delay: 5; }}
        .petal-3 {{ left: 80%; top: -12%; animation-duration: 32s; animation-delay: 10s; }}

        @keyframes fallDrift {{
            0% {{
                transform: translateY(-10vh) translateX(0px) rotate(0deg);
            }}
            25% {{
                transform: translateY(25vh) translateX(20px) rotate(35deg);
            }}
            50% {{
                transform: translateY(50vh) translateX(-15px) rotate(85deg);
            }}
            75% {{
                transform: translateY(75vh) translateX(18px) rotate(140deg);
            }}
            100% {{
                transform: translateY(110vh) translateX(-10px) rotate(200deg);
            }}
        }}
        </style>

        <div class="petal-overlay">
            <div class="petal petal-1"><img src="data:image/png;base64,{encoded}" /></div>
            <div class="petal petal-2"><img src="data:image/png;base64,{encoded}" /></div>
            <div class="petal petal-3"><img src="data:image/png;base64,{encoded}" /></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Page configuration
st.set_page_config(page_title="Seasonal Japan", page_icon="🌸", layout="wide")
add_bg_from_local("dashboards/assets/sakura_blurred.png")
add_floating_petals("dashboards/assets/sakura_petal.png")

st.markdown("""
<style>
html, body, [class*="css"]  {
    font-weight: 300 !important;
    letter-spacing: 0.2px;
    color: #5B4D53;
}

/* Headings */
h1, h2, h3 {
    font-weight: 300 !important;
}

/* Labels (selectboxes etc.) */
label {
    font-weight: 300;
}

/* Metrics (numbers + labels) */
[data-testid="stMetricValue"] {
    font-weight: 300;
}
[data-testid="stMetricLabel"] {
    font-weight: 300;
}
</style>
""", unsafe_allow_html=True)

# Function for consistent chart styling
def style_fig(fig):
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        title_x=0.05,
        margin=dict(l=40, r=40, t=60, b=40),

        # Background
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",

        # Global font (plus léger visuellement)
        font=dict(
            family="Helvetica Neue, Helvetica, Arial, sans-serif",
            size=12,
            color="#5B4D53"
        ),

        # Title styling (important car indépendant)
        title_font=dict(
            size=16,
            color="#5B4D53"
        )
    )

    # Axes (minimal clean look)
    fig.update_xaxes(
        showgrid=False,
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False
    )

    return fig

# App title & description
st.markdown("""
<div class="hero-block">
    <h1>When Will Sakura Bloom This Year?</h1>
    <p>
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

# Filter for station
options = list(station_label_map.keys())
default_index = options.index("Tokyo") if "Tokyo" in options else 0
with filter_col1:
    selected_name = st.selectbox(
        "Please choose a station ▼",
        options=options,
        index=default_index
    )

# Filter for period
with filter_col2:
    selected_n_years = st.selectbox(
        "Display the last ... years ▼",
        options=[10, 20, 30, 50, 100],
        index=4 # set to longest period by default?
    )

selected_station_code = station_label_map[selected_name]
selected_location_code = str(int(selected_station_code) - 47000)

bloom_history_df = get_bloom_history(selected_location_code)
bloom_temp_df = get_bloom_temp_features(selected_station_code, selected_location_code)
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

# Prepare bloom history
if not bloom_history_df.empty:
    bloom_history_df["date_key"] = pd.to_datetime(bloom_history_df["date_key"])
    bloom_history_df["year"] = bloom_history_df["year"].astype(int)                                           

if not bloom_temp_df.empty:
    bloom_temp_df["date_key"] = pd.to_datetime(bloom_temp_df["date_key"])
    bloom_temp_df["year"] = bloom_temp_df["year"].astype(int)

# Filter to last n years based on bloom history if available, else climate data
if not bloom_history_df.empty:
    max_year = bloom_history_df["year"].max()
else:
    max_year = df["year"].max()

min_year_to_keep = max_year - selected_n_years + 1

if not bloom_history_df.empty:
    bloom_history_df = bloom_history_df[bloom_history_df["year"] >= min_year_to_keep]

if not bloom_temp_df.empty:
    bloom_temp_df = bloom_temp_df[bloom_temp_df["year"] >= min_year_to_keep]

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

# Historical sakura bloom dates
if bloom_history_df.empty:
    st.info("No historical sakura bloom dates found for this location.")
else:
    bloom_ts_fig = px.line(
        bloom_history_df,
        x="year",
        y="day_of_year",
        title=f"Historical Sakura Bloom Dates • Last {selected_n_years} Years",
        labels={
            "year": "Year",
            "day_of_year": "Bloom date (day of year)"
        },
        color_discrete_sequence=["#E8AFCF"]
    )
    bloom_ts_fig = style_fig(bloom_ts_fig)

    # Add forecast point (2026 for now)
    if not forecast_df.empty and pd.notna(forecast_df.loc[0, "predicted_day_of_year"]):
        forecast_year = int(forecast_df.loc[0, "forecast_year"])
        forecast_doy = float(forecast_df.loc[0, "predicted_day_of_year"])

        bloom_ts_fig.add_scatter(
            x=[forecast_year],
            y=[forecast_doy],
            mode="text",
            name="forecast",
            text=["🌸"],
            textfont=dict(size=20),
            showlegend=False
        )
    
    st.plotly_chart(bloom_ts_fig, width="stretch")

# Late-winter temperature vs bloom date
if bloom_temp_df.empty or bloom_temp_df["mean_temp_feb_mar"].isna().all():
    st.info("No matched temperature or bloom history data found for this station.")
else:
    bloom_scatter_fig = px.scatter(
        bloom_temp_df.dropna(subset=["mean_temp_feb_mar", "day_of_year"]),
        x="mean_temp_feb_mar",
        y="day_of_year",
        trendline="ols",
        title="Late-Winter Temperature vs Bloom Date",
        labels={
            "mean_temp_feb_mar": "Average temperature in February–March (°C)",
            "day_of_year": "Bloom date (day of year)"
        },
        hover_data=["year"]
    )
    bloom_scatter_fig = style_fig(bloom_scatter_fig)

    # Style the markers
    bloom_scatter_fig.update_traces(
        marker=dict(
            color="#E8AFCF",
            size=5,
            opacity=0.65,
            line=dict(width=0)
        ),
        selector=dict(mode="markers")
    )

    # Style the trend line
    bloom_scatter_fig.update_traces(
        line=dict(
            color="#D98BB8",
            width=2
        ),
        selector=dict(mode="lines")
    )

    st.plotly_chart(bloom_scatter_fig, width="stretch")

# Source footer
st.markdown("---")
st.caption(
    f"Source: Japan Meteorological Agency (JMA) • Forecast model — {model_label_map.get(model_name)} • Updated March 2026"
)