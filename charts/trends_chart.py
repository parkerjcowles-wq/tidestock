import plotly.graph_objects as go
import pandas as pd

_COLORS = ["#38bdf8", "#a78bfa", "#34d399", "#fb923c", "#f472b6"]


def build_trends_chart(df: pd.DataFrame, keywords: list) -> go.Figure:
    fig = go.Figure()
    for i, kw in enumerate(keywords):
        if kw not in df.columns:
            continue
        fig.add_trace(go.Scatter(
            x=df.index, y=df[kw],
            name=kw.title(),
            line=dict(color=_COLORS[i % len(_COLORS)], width=2),
            hovertemplate=f"{kw.title()}: %{{y}}<br>%{{x|%b %d}}<extra></extra>",
        ))
        mean_val = df[kw].mean()
        spikes = df[df[kw] > mean_val * 1.8]
        for idx, row in spikes.iterrows():
            fig.add_annotation(
                x=idx, y=row[kw],
                text="↑ spike", showarrow=False,
                font=dict(color=_COLORS[i % len(_COLORS)], size=10),
                yshift=12,
            )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        margin=dict(l=10, r=10, t=40, b=10), height=280,
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="Search Interest (0–100)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#94a3b8")),
        title=dict(text="Google Trends — Bait Keyword Velocity (90 days)", font=dict(color="#94a3b8", size=13)),
    )
    return fig
