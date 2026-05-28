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

from src.viz.cards import render_best_time_to_visit_card

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

html, body, [data-testid="stAppViewContainer"] {
    background-color: #EBE7E3 !important;
}

section.main {
    background-color: #EBE7E3 !important;
}

[data-testid="stHeader"] {
    background: transparent;
}

:root {
    --sakura-light: #E8B9C2;
    --sakura-medium: #EA9FAD;
    --sakura-bright: #EA5B75;
}

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
    border: 1px solid rgba(232, 185, 194, 0.32);
    border-radius: 22px;
    padding: 22px 24px;
    min-height: 420px;
    box-sizing: border-box;
    box-shadow: 0 14px 35px rgba(120, 86, 110, 0.08);
    backdrop-filter: blur(12px);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

.st-key-timeline_card h3,
.st-key-visit_card h3,
.st-key-highlights_card h3,
.st-key-spots_card h3 {
    font-size: 1.02rem;
    font-weight: 800;
    color: #171219;
    margin-top: 0!important;
    padding-top: 0!important;
    margin-bottom: 0.8rem;
    line-height: 1.2;
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

.best-visit-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    color: #171219;
    justify-content: space-between;
}

.best-visit-card h3 {
    font-size: 1.02rem;
    font-weight: 800;
    color: #171219;
    margin: 0 !important;
    padding: 0 !important;
    margin-bottom: 0.8rem !important;
    line-height: 1.2;
}

.best-visit-subtitle {
    color: #7d7784;
    font-size: 0.9rem;
    line-height: 1.45;
    margin: 0 0 1.15rem 0;
}

.visit-timeline-labels {
    position: relative;
    height: 40px;
    margin-top: 0.1rem;
}

.timeline-label {
    position: absolute;
    top: 2px;
    transform: translateX(-50%);
    text-align: center;
}

.timeline-label span {
    font-size: 0.70rem;
    line-height: 1;
    font-weight: 300;
    white-space: nowrap;
    display: block;
    text-align: center
}

.label-first {
    left: 25%;
}

.label-peak {
    left: 50%;
}

.label-best {
    left: 75%;
}

.label-first span {
    color: var(--sakura-light);
}

.label-peak span {
    color: var(--sakura-bright);
}

.label-best span {
    color: var(--sakura-medium);
}

.dotted-line {
    width: 1px;
    height: 18px;
    margin: 4px auto 0 auto;
    background-size: 1px 7px;
    background-repeat: repeat-y;
    opacity: 0.7;
}

.label-first .dotted-line {
    background-image: linear-gradient(
        to bottom,
        var(--sakura-light) 45%,
        rgba(255,255,255,0) 0%
    );
}

.label-peak .dotted-line {
    background-image: linear-gradient(
        to bottom,
        var(--sakura-bright) 45%,
        rgba(255,255,255,0) 0%
    );
}

.label-best .dotted-line {
    background-image: linear-gradient(
        to bottom,
        var(--sakura-medium) 45%,
        rgba(255,255,255,0) 0%
    );
}

.visit-timeline-wrap {
    position: relative;
    height: 42px;
    margin-top: 0.1rem;
}

.timeline-pale-track {
    position: absolute;
    left: 0;
    right: 0;
    top: 13px;
    height: 22px;
    border-radius: 999px;
    background: rgba(232, 185, 194, 0.45);
}

.timeline-visit-window {
    position: absolute;
    left: 25%;
    right: 10%;
    top: 13px;
    height: 22px;
    border-radius: 999px;
    background: rgba(234, 159, 173, 0.62);
}

.timeline-peak-window {
    position: absolute;
    left: 35%;
    right: 38%;
    top: 17px;
    height: 14px;
    border-radius: 999px;
    background: var(--sakura-bright);
}

.timeline-dot {
    position: absolute;
    top: 10px;
    width: 7px;
    height: 7px;
    border-radius: 999px;
    transform: translateX(-50%);
    z-index: 5;
}

.dot-first {
    left: 25%;
    background: var(--sakura-light);
}

.dot-peak {
    left: 50%;
    background: var(--sakura-bright);
}

.dot-best {
    left: 75%;
    background: var(--sakura-medium);
}

.timeline-axis {
    position: relative;
    height: 52px;
    margin: 0.45rem 0 0.8rem 0;
}

.axis-line {
    position: absolute;
    top: 10px;
    left: 0;
    right: 0;
    height: 1px;
    background: rgba(232, 185, 194, 0.50);
}

.axis-tick {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    text-align: center;
}

.tick-one {
    left: 12%;
}

.tick-two {
    left: 38%;
}

.tick-three {
    left: 64%;
}

.tick-four {
    left: 92%;
}

.tick-mark {
    width: 1px;
    height: 17px;
    margin: 0 auto 7px auto;
    background: rgba(145, 151, 160, 0.55);
}

.tick-date {
    font-size: 0.76rem;
    line-height: 1.18;
    font-weight: 700;
    color: #5B4D53;
}

.visit-detail-section {
    margin-top: auto;
}

.visit-detail-row {
    display: grid;
    grid-template-columns: 10px minmax(0, 1fr);
    gap: 0.65rem;
    align-items: start;
    padding: 0.25rem 0;
}

.visit-detail-dot {
    width: 8px;
    height: 8px;
    margin-top: 0.45rem;
    border-radius: 999px;
    background: var(--sakura-light);
}

.visit-detail-dot.medium {
    background: var(--sakura-medium);
}

.visit-detail-dot.bright {
    background: var(--sakura-bright);
}

.visit-detail-label {
    font-size: 0.8rem;
    color: #7d7784;
    font-weight: 500;
    margin-bottom: 0.2rem;
}

.visit-detail-value {
    font-size: 0.9rem;
    line-height: 1.25;
    color: #171219;
    font-weight: 800;
    white-space: nowrap;
}

.visit-row-line {
    height: 1px;
    background: rgba(232, 185, 194, 0.45);
    margin: 0.4rem 0;
}

div[data-testid="column"] {
    display: flex;
    align-self: stretch;
}

div[data-testid="column"] > div {
    width: 100%;
}

.forecast-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: var(--sakura-light);
    display: inline-block;
    flex-shrink: 0;
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
                Plan your perfect trip across Japan with<br>
                bloom forecasts, peak viewing windows,<br>
                local highlights, and top spots to admire<br>
                the fleeting beauty of cherry blossoms.
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
selected_n_years = 20

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

reference_year = 2026

if not forecast_df.empty:
    reference_year = int(forecast_df.loc[0, "forecast_year"])

min_year_to_keep = reference_year - selected_n_years + 1

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

lower_col1, lower_col2, lower_col3, lower_col4 = st.columns([1, 1, 1, 1])

with lower_col1:
    with st.container(key="timeline_card"):
        st.markdown(f"### Through the Years")

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
        st.html(
            render_best_time_to_visit_card(
                station_name=selected_name,
                forecast_df=forecast_df,
            )
        )

with lower_col3:
    with st.container(key="highlights_card"):
        st.markdown(f"### Local Spring Traditions")
        st.markdown(
            '<p class="muted-text">Coming next...</p>', 
            unsafe_allow_html=True,
        )

with lower_col4:
    with st.container(key="spots_card"):
        st.markdown("### Nearby Gems")
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