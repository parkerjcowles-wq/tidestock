import plotly.graph_objects as go
import pandas as pd


def build_tide_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["height"],
        fill="tozeroy",
        line=dict(color="#38bdf8", width=2),
        fillcolor="rgba(56, 189, 248, 0.2)",
        hovertemplate="%{x|%a %I:%M %p}<br>Height: %{y:.1f} ft<extra></extra>",
        name="Tide Height",
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="Height (ft)"),
        title=dict(text="7-Day Tide Predictions", font=dict(color="#94a3b8", size=13)),
        height=250,
    )
    return fig
