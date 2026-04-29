import pandas as pd
import plotly.express as px

def plot_sakura_forecast_map(df: pd.DataFrame):
    df = df.copy()

    df["hover_title"] = df["station_name"].str.title()
    df["hover_bloom"] = "🌸 " + df["bloom_label"]
    df["hover_model"] = df["model_name"].str.replace("_", " ").str.title()

    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="predicted_day_of_year",
        hover_name="hover_title",
        hover_data={
            "station_code": True,
            "location_code": True,
            "hover_bloom": True,
            "hover_model": True,
            "mae_days": ":.1f",
            "rmse_days": ":.1f",
            "latitude": False,
            "longitude": False,
            "predicted_day_of_year": False,
            "model_name": False,
            "station_name": False,
            "bloom_label": False,
        },
        color_continuous_scale=[
            "#F2E6B8", 
            "#F1CCA6", 
            "#F2BFB4",
            "#F28695",
            "#C9B6E4",
        ],
        zoom=3,
        center={"lat": 36.5, "lon": 138.0},
        height=560,
    )

    fig.update_traces(
        marker=dict(
            size=15,
            opacity=0.92,
        ),
        hovertemplate=(
            "<b>%{hovertext}</b><br><br>"
            "%{customdata[2]}<br>"
            "Model: %{customdata[3]}<br>"
            # "MAE: %{customdata[4]} days<br>"
            # "RMSE: %{customdata[5]} days"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        title=dict(
            text="Forecasted Sakura Bloom Dates Across Japan",
        ),
        mapbox_style="white-bg",
        mapbox=dict(
            style="white-bg",
            center=dict(lat=36.5, lon=138.0),
            zoom=3,
            layers=[
                {
                    "source": "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json",
                    "type": "line",
                    "color": "rgba(130, 110, 120, 0.35)",
                    "line": {"width": 0.8},
                },
            ],
        ),

        margin=dict(l=0, r=0, t=70, b=0),

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Helvetica Neue, Helvetica, Arial, sans-serif",
            color="#000000"
        ),
        coloraxis_colorbar=dict(
            title=dict(
                text="Bloom<br>timing",
                font=dict(color="#000000")
            ),
            thickness=14,
            len=0.55,
            x=0.98,
            y=0.5,
            outlinewidth=0,
            tickfont=dict(color="#000000")
        ),
    )

    return fig