import plotly.graph_objects as go
import pandas as pd

_TREND_COLORS = {"rising": "#22c55e", "stable": "#fbbf24", "falling": "#ef4444"}
_TREND_DESC = {
    "rising":  "Rising — post-front recovery, improving bite",
    "stable":  "Stable — consistent bite",
    "falling": "Falling — approaching front, fish feed aggressively before storm",
}


def build_pressure_chart(df: pd.DataFrame, trend: str) -> go.Figure:
    color = _TREND_COLORS.get(trend, "#94a3b8")
    desc  = _TREND_DESC.get(trend, "")
    fig = go.Figure()

    if df.empty:
        fig.add_annotation(
            text="Pressure data unavailable — weather API fallback",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color="#475569", size=13),
        )
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#111318", plot_bgcolor="#111318",
            height=240, margin=dict(l=40, r=10, t=50, b=30),
            title=dict(text="Barometric Pressure · 48h", font=dict(color="#94a3b8", size=13)),
        )
        return fig

    fig.add_trace(go.Scatter(
        x=df["time"], y=df["pressure"],
        line=dict(color=color, width=2.5),
        hovertemplate="<b>%{x|%a %b %d %I %p}</b><br>%{y:.1f} hPa<extra></extra>",
        name="Pressure",
    ))

    # Fishing threshold bands — no annotation_text to avoid overlap
    fig.add_hrect(y0=1018, y1=1040, fillcolor="rgba(34,197,94,0.07)", line_width=0)
    fig.add_hrect(y0=990,  y1=1008, fillcolor="rgba(239,68,68,0.07)",  line_width=0)

    # Band labels pinned to right edge of y-axis with dark background
    fig.add_annotation(
        text="High pressure — good fishing",
        x=1.0, xref="paper", y=1029, yref="y",
        showarrow=False, font=dict(size=9, color="#4ade80"),
        xanchor="right", yanchor="middle",
        bgcolor="rgba(15,23,42,0.75)", borderpad=3,
    )
    fig.add_annotation(
        text="Low pressure — slow bite",
        x=1.0, xref="paper", y=999, yref="y",
        showarrow=False, font=dict(size=9, color="#f87171"),
        xanchor="right", yanchor="middle",
        bgcolor="rgba(15,23,42,0.75)", borderpad=3,
    )

    # Trend description above chart — paper coordinates, right-aligned
    fig.add_annotation(
        text=desc,
        xref="paper", yref="paper",
        x=1.0, y=1.0, xanchor="right", yanchor="bottom",
        showarrow=False, font=dict(size=10, color=color),
    )

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#111318", plot_bgcolor="#111318",
        margin=dict(l=40, r=10, t=50, b=30),
        height=250,
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="hPa"),
        title=dict(text="Barometric Pressure · 48h", font=dict(color=color, size=13)),
    )
    return fig
