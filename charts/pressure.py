import plotly.graph_objects as go
import pandas as pd

_TREND_COLORS = {"rising": "#22c55e", "stable": "#fbbf24", "falling": "#ef4444"}


def build_pressure_chart(df: pd.DataFrame, trend: str) -> go.Figure:
    color = _TREND_COLORS.get(trend, "#94a3b8")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["pressure"],
        line=dict(color=color, width=2),
        hovertemplate="%{x|%a %I %p}<br>%{y:.1f} hPa<extra></extra>",
        name="Pressure",
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="hPa"),
        title=dict(text=f"Barometric Pressure — {trend.capitalize()}", font=dict(color=color, size=13)),
        height=200,
    )
    return fig
