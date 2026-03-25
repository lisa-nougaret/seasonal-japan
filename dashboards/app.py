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

        /* Add white overlay for readability */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(247, 244, 242, 0.85);
            z-index: -1;
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
            width: 20px;
            opacity: 1;
            animation-name: fallDrift;
            animation-timing-function: linear;
            animation-iteration-count: infinite;
        }}

        .petal img {{
            width: 100%;
            display: block;
            filter: blur(0px);
        }}

        .petal-1 {{ left: 8%; top: -10%; animation-duration: 18s; animation-delay: 0s; }}
        .petal-2 {{ left: 22%; top: -15%; animation-duration: 22s; animation-delay: 4s; }}
        .petal-3 {{ left: 48%; top: -12%; animation-duration: 20s; animation-delay: 2s; }}
        .petal-4 {{ left: 67%; top: -18%; animation-duration: 24s; animation-delay: 7s; }}
        .petal-5 {{ left: 82%; top: -14%; animation-duration: 19s; animation-delay: 1s; }}

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
            <div class="petal petal-4"><img src="data:image/png;base64,{encoded}" /></div>
            <div class="petal petal-5"><img src="data:image/png;base64,{encoded}" /></div>
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
    letter-spacing: 0.2px
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

    # Line style
    fig.update_traces(
        line=dict(color="#E8AFCF", width=2),
        selector=dict(type="scatter")
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

with filter_col1:
    selected_name = st.selectbox(
        "Please choose a station ▼",
        options=list(station_label_map.keys())
    )

with filter_col2:
    selected_n_years = st.selectbox(
        "Display the last ... years ▼",
        options=[10, 20, 30, 50, 100],
        index=0 # set to shortest period by default
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