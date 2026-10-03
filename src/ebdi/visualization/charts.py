"""Charts share explicit metric labels and sample/denominator hover details."""

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ebdi.metrics.rates import DENOMINATORS, INCIDENTS

PALETTE = ["#163b4c", "#cd693e", "#3a8d91", "#d5b662"]


def style(fig: go.Figure, title: str | None = None) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        font={"family": "Arial", "color": "#163b4c"},
        title=title,
        margin={"l": 12, "r": 12, "t": 50, "b": 35},
        colorway=PALETTE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def label(metric: str) -> str:
    if "_per_100k_" in metric:
        incident, denominator = metric.split("_per_100k_")
        return f"{INCIDENTS[incident]} por 100.000 · {DENOMINATORS[denominator]}"
    return INCIDENTS.get(metric, metric.replace("_", " "))


def ranking(frame: pd.DataFrame, metric: str, top: int = 20) -> go.Figure:
    df = frame.dropna(subset=[metric]).nlargest(top, metric).sort_values(metric)
    error_args = {}
    if f"{metric}_upper" in df:
        df = df.copy()
        df["error_plus"] = df[f"{metric}_upper"] - df[metric]
        df["error_minus"] = df[metric] - df[f"{metric}_lower"]
        error_args = {"error_x": "error_plus", "error_x_minus": "error_minus"}
    fig = px.bar(
        df,
        x=metric,
        y="province",
        orientation="h",
        hover_data=["injury_crashes", "population", "unknown_collision"],
        color_discrete_sequence=[PALETTE[0]],
        **error_args,
    )
    fig.update_layout(height=max(440, top * 24), xaxis_title=label(metric), yaxis_title=None)
    return style(fig)


def choropleth(frame: pd.DataFrame, metric: str, geojson: dict[str, Any]) -> go.Figure:
    fig = px.choropleth(
        frame,
        geojson=geojson,
        locations="province_code",
        featureidkey="properties.province_code",
        color=metric,
        hover_name="province",
        hover_data={
            "province_code": False,
            "injury_crashes": True,
            "population": True,
            "unknown_collision": True,
        },
        color_continuous_scale=["#e8efeb", "#568993", "#163b4c"],
    )
    fig.update_geos(fitbounds="locations", visible=False, projection_type="mercator")
    fig.update_layout(height=500, coloraxis_colorbar={"title": "por 100.000"})
    return style(fig)
