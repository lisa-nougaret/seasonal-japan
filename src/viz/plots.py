import pandas as pd
import plotly.express as px

def plot_sakura_forecast_map(df: pd.DataFrame):
    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        color="predicted_day_of_year",
        hover_name="station_name",
        hover_data={
            "latitude": False,
            "longitude": False,
            "bloom_label": True,
            "predicted_day_of_year": False,
            "model_name": False,
            "mae_days": False,
            "rmse_days": False,
        },
        color_continuous_scale=[
        "#fde0ef",
        "#f9b4d0",
        "#f768a1",
        "#c51b8a",
        "#7a0177"
        ],
        projection="mercator",
    )

    fig.update_traces(
        marker=dict(
            size=11,
            opacity=0.9,
            line=dict(width=0.8, color="white")
        ),
        customdata=df[["hover_text"]],
        hovertemplate="%{customdata[0]}<extra></extra>",
    )

    fig.update_geos(
        fitbounds="locations",
        showland=True,
        landcolor="rgb(247, 244, 246)",
        showocean=True,
        oceancolor="rgb(252, 249, 251)",
        showcountries=False,
        showcoastlines=True,
        coastlinecolor="rgba(120,120,120,0.35)",
        lataxis_range=[24, 47],
        lonaxis_range=[122, 147],
        bgcolor="rgba(0,0,0,0)"
    )

    fig.update_layout(
        title="Forecasted Sakura Bloom Dates Across Japan",
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title="Bloom day<br>of year"
        ),
        height=700
    )

    return fig