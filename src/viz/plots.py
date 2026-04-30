import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

def plot_sakura_forecast_map(df: pd.DataFrame):
    df = df.copy()

    geojson_path = Path("dashboards/assets/japan.geojson")

    with open(geojson_path, "r", encoding="utf-8") as f:
        japan_geojson = json.load(f)

    df["hover_title"] = df["station_name"].str.title()
    df["hover_bloom"] = "🌸 " + df["bloom_label"]
    df["hover_uncertainty"] = "± " + df["mae_days"].round(1).astype(str) + " days"

    fig = go.Figure()

    # Japan silhouette
    fig.add_trace(
        go.Choropleth(
            geojson=japan_geojson,
            locations=["JPN"],
            z=[1],
            featureidkey="id",
            colorscale=[[0, "rgba(255,255,255,0.65)"], [1, "rgba(255,255,255,0.65)"]],
            marker_line_color="rgba(130, 110, 120, 0.45)",
            marker_line_width=1.1,
            showscale=False,
            hoverinfo="skip",
        )
    )

    # Sakura forecast points
    fig.add_trace(
        go.Scattergeo(
            lat=df["latitude"],
            lon=df["longitude"],
            mode="markers",
            text=df["hover_title"],
            customdata=df[
                [
                    "station_code",
                    "location_code",
                    "hover_bloom",
                    "hover_uncertainty",
                    "mae_days",
                    "rmse_days",
                ]
            ],
            marker=dict(
                size=15,
                opacity=0.92,
                color=df["predicted_day_of_year"],
                colorscale=[
                    [0.00, "#F2E6B8"],
                    [0.25, "#F1CCA6"],
                    [0.50, "#F2BFB4"],
                    [0.75, "#F28695"],
                    [1.00, "#C9B6E4"],
                ],
                colorbar=dict(
                    title=dict(text="Bloom<br>timing", font=dict(color="#000000")),
                    thickness=14,
                    len=0.55,
                    x=0.98,
                    y=0.5,
                    outlinewidth=0,
                    tickfont=dict(color="#000000"),
                ),
            ),
            hovertemplate=(
                "<span style='font-size:18px; font-weight:400;'>%{text}</span><br>"
                "<span style='font-size:14px;'>%{customdata[2]}</span><br>"
                "<span style='font-size:12px; color:#777;'>%{customdata[3]}</span>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(text="Forecasted Sakura Bloom Dates Across Japan"),
        height=620,
        margin=dict(l=0, r=0, t=70, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        clickmode="event+select",
        geo=dict(
            projection_type="mercator",
            showland=False,
            showocean=False,
            showlakes=False,
            showrivers=False,
            showcountries=False,
            showcoastlines=False,
            showframe=False,
            bgcolor="rgba(0,0,0,0)",
            fitbounds="locations",
            lonaxis=dict(range=[122, 154]),
            lataxis=dict(range=[24, 46]),
        ),
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.70)",
            bordercolor="rgba(200, 200, 200, 0)",
            font=dict(
                color="#000000",
                family="Arial, sans-serif",
                size=14,
            ),
        ),
    )

    return fig