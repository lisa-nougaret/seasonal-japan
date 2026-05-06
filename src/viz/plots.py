import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

def plot_sakura_forecast_map(df: pd.DataFrame):
    df = df.copy()
    min_val = df["predicted_day_of_year"].min()
    max_val = df["predicted_day_of_year"].max()
    tickvals = np.linspace(min_val, max_val, 3)

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
                    # title=dict(
                        # text="Bloom<br>timing", 
                        # side="top",
                        # font=dict(color="#000000", size=10),
                        # ),
                    orientation="h",
                    thickness=12,
                    len=0.16,
                    x=0.73,
                    xanchor="center",
                    y=0.10,
                    yanchor="bottom",
                    outlinewidth=0,
                    tickmode="array",
                    tickvals=tickvals,
                    ticktext=["early", "mid", "late"],
                    tickfont=dict(color="#000000", size=10),
                    ticks="",
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
        height=430,
        margin=dict(l=0, r=0, t=70, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        clickmode="event+select",
        geo=dict(
            domain=dict(x=[0, 1], y=[0.02, 0.98]), # to freeze map position
            projection_type="mercator",
            showland=False,
            showocean=False,
            showlakes=False,
            showrivers=False,
            showcountries=False,
            showcoastlines=False,
            showframe=False,
            bgcolor="rgba(0,0,0,0)",
            lonaxis=dict(range=[120, 150]),
            lataxis=dict(range=[23, 47]),
        ),
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="rgba(200, 200, 200, 0)",
            font=dict(
                color="#000000",
                family="Arial, sans-serif",
                size=14,
            ),
        ),
    )

    return fig