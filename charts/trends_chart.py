import plotly.graph_objects as go
import pandas as pd

_COLORS = ["#38bdf8", "#a78bfa", "#34d399", "#fb923c", "#f472b6"]


def _empty_fig(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(color="#475569", size=13), align="center",
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        height=280, margin=dict(l=10, r=10, t=40, b=10),
        title=dict(
            text="Google Trends — Bait Keyword Search Velocity (90 days)",
            font=dict(color="#94a3b8", size=13),
        ),
    )
    return fig


def build_trends_chart(df: pd.DataFrame, keywords: list) -> go.Figure:
    if df is None or df.empty:
        return _empty_fig(
            "Google Trends data unavailable<br>"
            "<span style='font-size:11px'>Rate limited or API timeout — try refreshing in a few minutes</span>"
        )

    fig = go.Figure()
    for i, kw in enumerate(keywords):
        if kw not in df.columns:
            continue
        color = _COLORS[i % len(_COLORS)]
        fig.add_trace(go.Scatter(
            x=df.index, y=df[kw],
            name=kw.title(),
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{kw.title()}</b>: %{{y}}<br>%{{x|%b %d, %Y}}<extra></extra>",
        ))
        # Annotate only the single largest spike per keyword
        mean_val = df[kw].mean()
        spikes = df[df[kw] > mean_val * 1.8]
        if not spikes.empty:
            peak_idx = spikes[kw].idxmax()
            peak_val  = spikes.loc[peak_idx, kw]
            fig.add_annotation(
                x=peak_idx, y=peak_val,
                text=f"↑ {kw.split()[0].title()}",
                showarrow=False,
                font=dict(color=color, size=10),
                yshift=14,
                bgcolor="rgba(15,23,42,0.8)",
                bordercolor=color, borderwidth=1, borderpad=3,
            )

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        margin=dict(l=10, r=10, t=50, b=10), height=280,
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="Search Interest (0–100)"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            font=dict(color="#94a3b8", size=11),
        ),
        title=dict(
            text="Google Trends — Bait Keyword Search Velocity (90 days)",
            font=dict(color="#94a3b8", size=13),
        ),
    )
    return fig
