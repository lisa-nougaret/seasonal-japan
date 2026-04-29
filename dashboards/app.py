# Run with streamlit run dashboards/app.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import base64
import streamlit as st
import pandas as pd
import plotly.express as px

from src.viz.dashboard_queries import (
    get_station_list,
    get_climate_timeseries,
    get_climate_kpis,
    get_bloom_forecast,
    get_bloom_history,
    get_bloom_temp_features,
    get_sakura_forecast_map,
)

from src.viz.plots import plot_sakura_forecast_map

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

        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba(247, 244, 242, 0.1);
            z-index: 0;
        }}

        .stApp > div {{
            position: relative;
            z-index: 1;
        }}
        </style>
        """,
        unsafe_allow_html=True,
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

.block-container {
    max-width: 100% !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
}

[data-testid="stPlotlyChart"] {
    background: linear-gradient(
        135deg,
        rgba(242, 230, 184, 0.55),
        rgba(242, 191, 180, 0.50),
        rgba(201, 182, 228, 0.45)
    );
    border-radius: 28px;
    padding: 1rem;
    box-shadow: 0 25px 70px rgba(200, 86, 112, 0.18);
    backdrop-filter: blur(4px);
    overflow: hidden;
}

    /* Remove internal rectangular background */
[data-testid="stPlotlyChart"] > div,
[data-testid="stPlotlyChart"] .js-plotly-plot,
[data-testid="stPlotlyChart"] .plot-container,
[data-testid="stPlotlyChart"] .svg-container {
    background: transparent !important;
}        

h1, h2, h3 {
    font-weight: 300 !important;
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
""", unsafe_allow_html=True)

def style_fig(fig):
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        title_x=0.05,
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Helvetica Neue, Helvetica, Arial, sans-serif",
            size=12,
            color="#5B4D53",
        ),
        title_font=dict(size=16, color="#5B4D53"),
    )

    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)

    return fig

# Hero
st.markdown("""
<div class="hero-block">
    <h1>When Will Sakura Bloom This Year?</h1>
    <p>
        Explore historical temperature patterns and forecasted sakura first bloom dates, across Japan.
    </p>
</div>
""", unsafe_allow_html=True)

# Map first
map_df = get_sakura_forecast_map(year=2026)

clicked_station_code = None

if map_df.empty:
    st.info("No forecast map data available.")
else:
    fig_map = plot_sakura_forecast_map(map_df)
    map_event = st.plotly_chart(
        fig_map,
        width='stretch',
        key="sakura_map",
        on_select="rerun",
        selection_mode="points",
    )

    if map_event and map_event.selection.points:
        clicked_point = map_event.selection.points[0]
        clicked_station_code = str(clicked_point["customdata"][0])

# Load stations
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

# Initialize selected station once
if "selected_station_name" not in st.session_state:
    st.session_state["selected_station_name"] = options[default_index]

# Update selected station from map click
if clicked_station_code and clicked_station_code in reverse_station_label_map:
    st.session_state["selected_station_name"] = reverse_station_label_map[clicked_station_code]

# Final selected station used by KPIs and charts
selected_name = st.session_state["selected_station_name"]

st.markdown(f"""Selected station: {selected_name.title()}""")

selected_n_years = 100

selected_station_code = station_label_map[selected_name]
selected_location_code = str(int(selected_station_code) - 47000)

bloom_history_df = get_bloom_history(selected_location_code)
bloom_temp_df = get_bloom_temp_features(selected_station_code, selected_location_code)
forecast_df = get_bloom_forecast(selected_location_code, year=2026)

df = get_climate_timeseries(selected_station_code)
kpi_df = get_climate_kpis(selected_station_code)

if df.empty:
    st.warning("No climate data found for this station.")
    st.stop()

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

# KPI row
kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric("Forecasted bloom date", bloom_date)
kpi2.metric("Average temperature (°C)", kpi_df.loc[0, "avg_temp_c"])
kpi3.metric(
    "Temperature range (°C)",
    f"{kpi_df.loc[0, 'min_temp_c']} to {kpi_df.loc[0, 'max_temp_c']}",
)

# Charts row
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
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
                "day_of_year": "Bloom date (day of year)",
            },
            color_discrete_sequence=["#E8AFCF"],
        )
        bloom_ts_fig = style_fig(bloom_ts_fig)

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
                showlegend=False,
            )

        st.plotly_chart(bloom_ts_fig, width='stretch')

with chart_col2:
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
                "day_of_year": "Bloom date (day of year)",
            },
            hover_data=["year"],
        )
        bloom_scatter_fig = style_fig(bloom_scatter_fig)

        bloom_scatter_fig.update_traces(
            marker=dict(
                color="#E8AFCF",
                size=5,
                opacity=0.65,
                line=dict(width=0),
            ),
            selector=dict(mode="markers"),
        )

        bloom_scatter_fig.update_traces(
            line=dict(color="#D98BB8", width=2),
            selector=dict(mode="lines"),
        )

        st.plotly_chart(bloom_scatter_fig, width='stretch')

st.markdown("---")
st.caption(
    f"Source: Japan Meteorological Agency (JMA) • Forecast model — {model_label_map.get(model_name, model_name)} • Updated {forecast_updated_at}"
)