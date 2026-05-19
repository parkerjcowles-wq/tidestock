import plotly.graph_objects as go
import pandas as pd

_TREND_COLORS = {"rising": "#22c55e", "stable": "#fbbf24", "falling": "#ef4444"}
_TREND_DESC = {
    "rising":  "Rising → fish more active",
    "stable":  "Stable → consistent bite",
    "falling": "Falling → pre-storm slowdown",
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
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            height=200, margin=dict(l=10, r=10, t=40, b=10),
            title=dict(text="Barometric Pressure (48h)", font=dict(color="#94a3b8", size=13)),
        )
        return fig

    fig.add_trace(go.Scatter(
        x=df["time"], y=df["pressure"],
        line=dict(color=color, width=2),
        hovertemplate="<b>%{x|%a %b %d %I %p}</b><br>Pressure: <b>%{y:.1f} hPa</b><extra></extra>",
        name="Pressure",
    ))

    # Fishing threshold bands
    fig.add_hrect(
        y0=1018, y1=1040,
        fillcolor="rgba(34, 197, 94, 0.07)", line_width=0,
        annotation_text="High pressure (good fishing)",
        annotation_position="top left",
        annotation_font=dict(size=9, color="#4ade80"),
    )
    fig.add_hrect(
        y0=990, y1=1008,
        fillcolor="rgba(239, 68, 68, 0.07)", line_width=0,
        annotation_text="Low pressure (poor fishing)",
        annotation_position="bottom left",
        annotation_font=dict(size=9, color="#f87171"),
    )

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="hPa"),
        title=dict(
            text=f"Barometric Pressure (48h) — {trend.capitalize()} · {desc}",
            font=dict(color=color, size=13),
        ),
        height=220,
    )
    return fig
