import pandas as pd
import streamlit as st
import plotly.express as px
from src.viz.dashboard_queries import (
    get_station_list,
    get_climate_timeseries,
    get_climate_kpis,
)

st.set_page_config(page_title="Seasonal Japan", layout="wide")

st.title("Seasonal Japan 🌸")
st.markdown("Explore long-term monthly climate patterns across Japan.")

stations = get_station_list()

station_label_map = {
    f"{row['station_name']} ({row['station_code']})": row["station_code"]
    for _, row in stations.iterrows()
}

selected_label = st.selectbox(
    "Please choose a station ▼",
    options=list(station_label_map.keys())
)

selected_station_code = station_label_map[selected_label]

df = get_climate_timeseries(selected_station_code)
kpi_df = get_climate_kpis(selected_station_code)

if df.empty:
    st.warning("No data found for this station.")
    st.stop()

station_name = df["station_name"].dropna().iloc[0]

st.subheader(f"Station • {station_name}")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Years", int(kpi_df.loc[0, "total_years"]))
col2.metric("Average temperature (°C)", kpi_df.loc[0, "avg_temp_c"])
col3.metric("Average precipitation (mm)", kpi_df.loc[0, "avg_precipitation_mm"])
col4.metric("Minimum temperature (°C)", kpi_df.loc[0, "min_temp_c"])
col5.metric("Maximum temperature (°C)", kpi_df.loc[0, "max_temp_c"])

temp_fig = px.line(
    df,
    x="date_key",
    y="mean_temp_c",
    title=f"🌡️ Monthly Temperature • {station_name}",
    labels={
        "date_key": "Date",
        "mean_temp_c": "Average temperature (°C)"
    }
)

precip_fig = px.line(
    df,
    x="date_key",
    y="precipitation_mm",
    title=f"🌧️ Monthly Precipitation • {station_name}",
    labels={
        "date_key": "Date",
        "precipitation_mm": "Precipitation (mm)"
    }
)

seasonal_avg = (
    df.groupby("season", as_index=False)[["mean_temp_c", "precipitation_mm"]]
    .mean()
)

# Map season names to emojis for visualization
season_map = {
    "spring": "🌷",
    "summer": "☀️",
    "fall": "🍂",
    "winter": "🌨️"
}
seasonal_avg["season"] = seasonal_avg["season"].map(season_map)

# Map season names to colors for visualization
season_colors = {
    "🌷": "#DE52AF",  # Tulip pink
    "☀️": "#ECB633",  # Sun yellow
    "🍂": "#E0773B",    # Maple orange
    "🌨️": "#C7C3FF"   # Snowy purple
}

season_order = ["🌷", "☀️", "🍂", "🌨️"]
seasonal_avg["season"] = pd.Categorical(
    seasonal_avg["season"],
    categories=season_order,
    ordered=True
)
seasonal_avg = seasonal_avg.sort_values("season")

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

st.plotly_chart(temp_fig, use_container_width=True)
st.plotly_chart(precip_fig, use_container_width=True)
st.plotly_chart(season_temp_fig, use_container_width=True)

# with st.expander("Show raw data"):
#    st.dataframe(df, use_container_width=True)

# Run with: streamlit run dashboards/app.py