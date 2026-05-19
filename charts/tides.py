import plotly.graph_objects as go
import pandas as pd


def build_tide_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    if df.empty:
        fig.add_annotation(
            text="Tide data unavailable — NOAA API fallback active",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color="#475569", size=13),
        )
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            height=250, margin=dict(l=10, r=10, t=40, b=10),
            title=dict(text="7-Day Tide Predictions", font=dict(color="#94a3b8", size=13)),
        )
        return fig

    fig.add_trace(go.Scatter(
        x=df["time"], y=df["height"],
        fill="tozeroy",
        line=dict(color="#38bdf8", width=2),
        fillcolor="rgba(56, 189, 248, 0.15)",
        hovertemplate="<b>%{x|%a %b %d, %I:%M %p}</b><br>Tide: <b>%{y:.1f} ft</b><extra></extra>",
        name="Tide Height",
    ))

    # "Now" marker
    now = pd.Timestamp.now()
    if df["time"].min() <= now <= df["time"].max():
        fig.add_vline(
            x=now.timestamp() * 1000,
            line=dict(color="#fbbf24", dash="dot", width=1.5),
            annotation_text="Now",
            annotation_font=dict(color="#fbbf24", size=10),
            annotation_position="top right",
        )

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="Height (ft)", rangemode="tozero"),
        title=dict(
            text="7-Day Tide Predictions · Newburyport MA · NOAA Station 8440466",
            font=dict(color="#94a3b8", size=13),
        ),
        height=250,
    )
    return fig
