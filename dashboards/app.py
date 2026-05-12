# Run with streamlit run dashboards/app.py

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import base64
import streamlit as st
import pandas as pd

from src.viz.dashboard_queries import (
    get_station_list,
    get_climate_timeseries,
    get_bloom_forecast,
    get_bloom_history,
    get_bloom_temp_features,
    get_sakura_forecast_map,
)

from src.viz.plots import (
    plot_sakura_forecast_map,
    plot_sakura_bloom_timeline,
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

        .petal-1 {{ left: 15%; top: -10%; animation-duration: 28s; animation-delay: 0s; }}
        .petal-2 {{ left: 55%; top: -15%; animation-duration: 30s; animation-delay: 5s; }}
        .petal-3 {{ left: 80%; top: -12%; animation-duration: 32s; animation-delay: 10s; }}

        @keyframes fallDrift {{
            0% {{ transform: translateY(-10vh) translateX(0px) rotate(0deg); }}
            25% {{ transform: translateY(25vh) translateX(20px) rotate(35deg); }}
            50% {{ transform: translateY(50vh) translateX(-15px) rotate(85deg); }}
            75% {{ transform: translateY(75vh) translateX(18px) rotate(140deg); }}
            100% {{ transform: translateY(110vh) translateX(-10px) rotate(200deg); }}
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

st.set_page_config(
    page_title="Seasonal Japan", 
    page_icon="🌸", 
    layout="wide"
)

add_floating_petals("dashboards/assets/sakura_petal.png")

st.markdown(
    """
<style>
html, body, [class*="css"]  {
    font-weight: 300 !important;
    letter-spacing: 0.2px;
    color: #5B4D53;
}

.block-container {
    max-width: 100% !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
}

.hero-block {
    padding-top: 5rem;
    padding-left: 0.5rem;
}

.hero-block h1 {
    font-size: 2.6rem;
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: 0px;
    color: #050505;
    margin-bottom: 1.4rem;
}

.hero-block p {
    font-size: 0.95rem;
    line-height: 1.45;
    color: #777;
    margin-bottom: 2rem;
}

[data-testid="stPlotlyChart"] {
    background: transparent !important;
    border-radius: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    overflow: visible !important;
}

[data-testid="stPlotlyChart"] > div,
[data-testid="stPlotlyChart"] .js-plotly-plot,
[data-testid="stPlotlyChart"] .plot-container,
[data-testid="stPlotlyChart"] .svg-container {
    background: transparent !important;
}

.st-key-timeline_card,
.st-key-visit_card,
.st-key-highlights_card,
.st-key-spots_card {
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(255, 182, 213, 0.26);
    border-radius: 22px;
    padding: 22px 24px;
    min-height: 420px;
    box-shadow: 0 14px 35px rgba(120, 86, 110, 0.08);
    backdrop-filter: blur(12px);
}

.st-key-timeline_card h3,
.st-key-visit_card h3,
.st-key-highlights_card h3,
.st-key-spots_card h3 {
    font-size: 1.02rem;
    font-weight: 800;
    color: #171219;
    margin-bottom: 0.8rem;
}

.muted-text {
    color: #7d7784;
    font-size: 0.9rem;
    line-height: 1.5;
}

label {
    font-weight: 300;
}

[data-testid="stMetricValue"] {
    font-weight: 300;
}

[data-testid="stMetricLabel"] {
    font-weight: 300;
}
</style>
""",
    unsafe_allow_html=True,
)

# Stations

stations = get_station_list()

station_label_map = {
    row["station_name"]: row["station_code"]
    for _, row in stations.iterrows()
}

options = list(station_label_map.keys())
default_index = options.index("TOKYO") if "TOKYO" in options else 0

reverse_station_label_map = {
    str(v): k for k, v in station_label_map.items()
}

if "selected_station_name" not in st.session_state:
    st.session_state["selected_station_name"] = options[default_index]

selected_name = st.session_state["selected_station_name"]
selected_station_code = station_label_map[selected_name]

# Hero + Map

map_df = get_sakura_forecast_map(year=2026)
clicked_station_code = None

hero_left, hero_right = st.columns([0.75, 1.25], gap="large")

with hero_left:
    st.markdown(
        """
        <div class="hero-block">
            <h1>When Will Sakura<br>Bloom in Japan?</h1>
            <p>
                Explore forecasted sakura bloom dates<br>
                across Japan, along with historical<br>
                temperature patterns.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with hero_right:
    if map_df.empty:
        st.info("No forecast map data available.")
    else:
        fig_map = plot_sakura_forecast_map(
            map_df,
            selected_station_code=selected_station_code,
        )

        map_event = st.plotly_chart(
            fig_map,
            width="stretch",
            key="sakura_map",
            on_select="rerun",
            selection_mode="points",
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "doubleClick": False,
                "staticPlot": False,
            },
        )

        if map_event and map_event.selection.points:
            clicked_point = map_event.selection.points[0]
            clicked_station_code = str(clicked_point["customdata"][0])

# Update selected station based on map click

if (
    clicked_station_code
    and clicked_station_code in reverse_station_label_map
    and clicked_station_code != str(station_label_map[st.session_state["selected_station_name"]])
):
    st.session_state["selected_station_name"] = reverse_station_label_map[clicked_station_code]
    st.rerun()

# Final station state

selected_name = st.session_state["selected_station_name"]
selected_station_code = station_label_map[selected_name]
selected_location_code = str(int(selected_station_code) - 47000)
selected_n_years = 30

# Load data

bloom_history_df = get_bloom_history(selected_location_code)
bloom_temp_df = get_bloom_temp_features(selected_station_code, selected_location_code)
forecast_df = get_bloom_forecast(selected_location_code, year=2026)

df = get_climate_timeseries(selected_station_code)

if df.empty:
    st.warning("No climate data found for this station.")
    st.stop()

# Prepare data

df["date_key"] = pd.to_datetime(df["date_key"])
df["year"] = df["date_key"].dt.year

if not bloom_history_df.empty:
    bloom_history_df["date_key"] = pd.to_datetime(bloom_history_df["date_key"])
    bloom_history_df["year"] = bloom_history_df["year"].astype(int)

if not bloom_temp_df.empty:
    bloom_temp_df["date_key"] = pd.to_datetime(bloom_temp_df["date_key"])
    bloom_temp_df["year"] = bloom_temp_df["year"].astype(int)

if not bloom_history_df.empty:
    max_year = bloom_history_df["year"].max()
else:
    max_year = df["year"].max()

min_year_to_keep = max_year - selected_n_years + 1

if not bloom_history_df.empty:
    bloom_history_df = bloom_history_df[bloom_history_df["year"] >= min_year_to_keep]

if not bloom_temp_df.empty:
    bloom_temp_df = bloom_temp_df[bloom_temp_df["year"] >= min_year_to_keep]

# Forecast info

if not forecast_df.empty and pd.notna(forecast_df.loc[0, "predicted_event_date"]):
    bloom_date = pd.to_datetime(forecast_df.loc[0, "predicted_event_date"]).strftime("%d %b %Y")
    model_name = forecast_df.loc[0, "model_name"]
    forecast_updated_at = pd.to_datetime(forecast_df.loc[0, "trained_at"]).strftime("%d %b %Y")
else:
    bloom_date = "Not available"
    model_name = "Not available"
    forecast_updated_at = "Not available"

model_label_map = {
    "linear_regression": "Linear Regression",
    "random_forest": "Random Forest",
    "hist_gradient_boosting": "Histogram Gradient Boosting",
}

# Bottom section

lower_col1, lower_col2, lower_col3, lower_col4 = st.columns([1.5, 1, 1, 1])

with lower_col1:
    with st.container(key="timeline_card"):
        st.markdown(f"### Sakura Bloom Timeline • {selected_name.title()}")

        fig_timeline = plot_sakura_bloom_timeline(
            bloom_history_df,
            forecast_df,
        )

        st.plotly_chart(
            fig_timeline,
            width="stretch",
            config={"displayModeBar": False},
        )

with lower_col2:
    with st.container(key="visit_card"):
        st.markdown(f"### Best Time to Visit {selected_name.title()}")
        st.markdown(
            '<p class="muted-text">Coming next...</p>', 
            unsafe_allow_html=True,
        )

with lower_col3:
    with st.container(key="highlights_card"):
        st.markdown(f"### Spring Highlights in {selected_name.title()}")
        st.markdown(
            '<p class="muted-text">Coming next...</p>', 
            unsafe_allow_html=True,
        )

with lower_col4:
    with st.container(key="spots_card"):
        st.markdown("### Top Nearby Spots")
        st.markdown(
            '<p class="muted-text">Coming next...</p>', 
            unsafe_allow_html=True,
        )

st.markdown("---")
st.caption(
    f"Source: Japan Meteorological Agency (JMA) • "
    f"Forecast model — {model_label_map.get(model_name, model_name)} • "
    f"Updated {forecast_updated_at}"
)