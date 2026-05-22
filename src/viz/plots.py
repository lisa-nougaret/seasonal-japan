import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

SAKURA_LIGHT = "#E8B9C2"
SAKURA_MEDIUM = "#EA9FAD"
SAKURA_BRIGHT = "#EA5B75"

def plot_sakura_forecast_map(
    df: pd.DataFrame, 
    selected_station_code: str | None = None,
):
    df = df.copy()
    df["station_code"] = df["station_code"].astype(str)

    min_val = df["predicted_day_of_year"].min()
    max_val = df["predicted_day_of_year"].max()
    tickvals = np.linspace(min_val, max_val, 3)

    selected_station_code = str(selected_station_code) if selected_station_code is not None else None
    has_selected_station = selected_station_code in df["station_code"].values

    geojson_path = Path("dashboards/assets/japan.geojson")

    with open(geojson_path, "r", encoding="utf-8") as f:
        japan_geojson = json.load(f)

    df["hover_title"] = df["station_name"].str.title()
    df["hover_bloom"] = "🌸 " + df["bloom_label"]
    df["hover_uncertainty"] = "± " + df["mae_days"].round(1).astype(str) + " days"

    colorscale = [
        [0.00, "#F2E6B8"],
        [0.25, "#F1CCA6"],
        [0.50, "#F2BFB4"],
        [0.75, "#F28695"],
        [1.00, "#C9B6E4"],
    ]

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
            showlegend=False,
        )
    )

    # All stations, slightly faded when one station is selected
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
                opacity=0.90,
                color=df["predicted_day_of_year"],
                colorscale=colorscale,
                cmin=min_val,
                cmax=max_val,
                line=dict(width=0),
                colorbar=dict(
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
            showlegend=False,
        )
    )

    # Selected station, same color scale, outlined
    if has_selected_station:
        selected_df = df[df["station_code"] == selected_station_code]

        if not selected_df.empty:
            selected = selected_df.iloc[0]

            text_position = (
                "middle left"
                if selected["longitude"] > 140
                else "middle right"
            )

            fig.add_trace(
                go.Scattergeo(
                    lat=[selected["latitude"]],
                    lon=[selected["longitude"]],
                    mode="markers+text",
                    text=[
                        f"<b>{selected['hover_title']}</b>"
                    ],
                    customdata=[
                        [
                            selected["station_code"],
                            selected["location_code"],
                            selected["hover_bloom"],
                            selected["hover_uncertainty"],
                            selected["mae_days"],
                            selected["rmse_days"],
                        ]
                    ],
                    textposition=text_position,
                    textfont=dict(
                        size=14,
                        color="#050505",
                        family="Arial, sans-serif",
                    ),
                    marker=dict(
                        size=15,
                        opacity=1,
                        color=[selected["predicted_day_of_year"]],
                        colorscale=colorscale,
                        cmin=min_val,
                        cmax=max_val,
                        line=dict(
                            width=1.2,
                            color="rgba(0, 0, 0, 0.75)",
                        ),
                        showscale=False,
                    ),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=70, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        clickmode="event+select",
        showlegend=False,
        geo=dict(
            domain=dict(x=[0, 1], y=[0.02, 0.98]),
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

def plot_sakura_bloom_timeline(
    bloom_history_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
):
    fig = go.Figure()
    df = bloom_history_df.copy()

    def doy_to_label(day_of_year: int) -> str:
        return pd.Timestamp("2026-01-01") + pd.Timedelta(days=int(day_of_year) - 1)

    if not df.empty:
        df["date_key"] = pd.to_datetime(df["date_key"])
        df["year"] = df["year"].astype(int)
        df["day_of_year"] = pd.to_numeric(df["day_of_year"], errors="coerce")
        df = df.dropna(subset=["year", "day_of_year"]).sort_values("year")

        df["bloom_date_label"] = (
            pd.to_datetime(df["year"].astype(str), format="%Y")
            + pd.to_timedelta(df["day_of_year"] - 1, unit="D")
        ).dt.strftime("%d %b")

        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df["day_of_year"],
                mode="lines",
                name="Historical bloom",
                line=dict(color=SAKURA_LIGHT, width=2.2, shape="spline", smoothing=0.7),
                customdata=df["bloom_date_label"],

                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Bloom date: %{customdata}<extra></extra>"
                ),
            )
        )

    if not forecast_df.empty:
        forecast = forecast_df.iloc[0]

        forecast_year = int(forecast["forecast_year"])
        forecast_doy = float(forecast["predicted_day_of_year"])
        forecast_date = pd.to_datetime(forecast["predicted_event_date"])
        forecast_label = forecast_date.strftime("%d %b")

        fig.add_trace(
            go.Scatter(
                x=[forecast_year],
                y=[forecast_doy],
                mode="markers",
                name="Forecast",
                marker=dict(
                    size=12,
                    color="#000000",
                    symbol="circle",
                ),
                hovertemplate=(
                    "<b>Forecast bloom date</b><br>"
                    f"{forecast_date.strftime('%d %b %Y')}<extra></extra>"
                ),
            )
        )

        fig.add_annotation(
            x=forecast_year,
            y=forecast_doy,
            text=f"<b>{forecast_label}</b>",
            showarrow=False,
            xshift=0,
            yshift=18,
            font=dict(
                size=12, 
                color="#000000",
            ),
        )

    fig.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Helvetica Neue, Helvetica, Arial, sans-serif",
            color="#5B4D53",
            size=12,
        ),
        showlegend=False,
        hoverlabel=dict(
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="rgba(234, 159, 173, 0.35)",
            font=dict(color="#2F2930"),
        ),
    )

    x_min = forecast_year - 19
    x_max = forecast_year + 2

    fig.update_xaxes(
        title=None,
        range=[x_min, x_max],
        tickmode="array",
        tickvals=list(range(x_min, x_max + 1, 5)),
        showgrid=False,
        zeroline=False,
        tickfont=dict(color="#6F6A76", size=11),
    )

    y_tickvals = [70, 80, 90, 100]
    y_ticktext = [
        doy_to_label(v).strftime("%d %b").lstrip("0")
        for v in y_tickvals
    ]

    fig.update_yaxes(
        title=None,
        tickmode="array",
        tickvals=y_tickvals,
        ticktext=y_ticktext,
        showgrid=True,
        gridcolor="rgba(234, 159, 173, 0.13)",
        zeroline=False,
        tickfont=dict(color="#6F6A76", size=11),
    )

    return fig