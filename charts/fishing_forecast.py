import plotly.graph_objects as go
import datetime


def _project_day_score(moon_entry: dict, weather_entry: dict) -> int:
    score = moon_entry["score"]

    precip = weather_entry.get("precip_pct", 0)
    temp = weather_entry.get("temp_max", 65)
    wind = weather_entry.get("wind_mph", 0)

    if precip > 70:
        score -= 20
    elif precip >= 40:
        score -= 8

    if 52 <= temp <= 76:
        score += 8
    elif temp < 42 or temp > 90:
        score -= 12

    if wind > 25:
        score -= 15
    elif wind >= 18:
        score -= 6

    return max(0, min(100, score))


def build_fishing_forecast_chart(week_moon: list, forecast: list) -> go.Figure:
    days = list(zip(week_moon, forecast))

    x_labels = [f["dow"] for _, f in days]
    scores = [_project_day_score(m, f) for m, f in days]
    is_weekend = [f["is_weekend"] for _, f in days]
    emojis = [f.get("emoji", "") for _, f in days]

    avg = sum(scores) / len(scores) if scores else 0
    if avg >= 65:
        line_color = "#4ade80"
        fill_color = "rgba(74, 222, 128, 0.12)"
    elif avg >= 45:
        line_color = "#fbbf24"
        fill_color = "rgba(251, 191, 36, 0.12)"
    else:
        line_color = "#f87171"
        fill_color = "rgba(248, 113, 113, 0.12)"

    marker_symbols = ["diamond" if w else "circle" for w in is_weekend]
    marker_sizes = [12 if w else 8 for w in is_weekend]
    marker_colors = ["#fbbf24" if w else line_color for w in is_weekend]

    fig = go.Figure()

    # Background bands
    fig.add_hrect(y0=75, y1=110, fillcolor="rgba(74, 222, 128, 0.06)", line_width=0)
    fig.add_hrect(y0=50, y1=75, fillcolor="rgba(251, 191, 36, 0.06)", line_width=0)
    fig.add_hrect(y0=-20, y1=50, fillcolor="rgba(248, 113, 113, 0.06)", line_width=0)

    # Reference lines
    fig.add_hline(y=75, line=dict(color="#4ade80", dash="dot", width=1))
    fig.add_hline(y=50, line=dict(color="#fbbf24", dash="dot", width=1))

    # Weekend vertical reference lines
    for i, (label, weekend) in enumerate(zip(x_labels, is_weekend)):
        if weekend:
            fig.add_vline(
                x=label,
                line=dict(color="#2a2a2e", dash="dot", width=1.5),
            )

    # Filled area line trace
    fig.add_trace(go.Scatter(
        x=x_labels,
        y=scores,
        mode="lines+markers+text",
        line=dict(color=line_color, width=2),
        fill="tozeroy",
        fillcolor=fill_color,
        marker=dict(
            symbol=marker_symbols,
            size=marker_sizes,
            color=marker_colors,
            line=dict(width=0),
        ),
        text=[str(s) for s in scores],
        textposition="top center",
        textfont=dict(size=10, color="#f1f1f3"),
        hovertemplate="<b>%{x}</b><br>Fishing Score: %{y}/100<extra></extra>",
        name="Fishing Score",
    ))

    # Weather emoji annotations along the bottom
    for label, emoji in zip(x_labels, emojis):
        if emoji:
            fig.add_annotation(
                x=label,
                y=-14,
                yref="y",
                text=emoji,
                showarrow=False,
                font=dict(size=16),
                xanchor="center",
            )

    # Zone labels on right side
    fig.add_annotation(
        x=1.01, y=87, xref="paper", yref="y",
        text="Prime", showarrow=False,
        font=dict(size=9, color="#4ade80"),
        xanchor="left",
    )
    fig.add_annotation(
        x=1.01, y=62, xref="paper", yref="y",
        text="Good", showarrow=False,
        font=dict(size=9, color="#fbbf24"),
        xanchor="left",
    )
    fig.add_annotation(
        x=1.01, y=25, xref="paper", yref="y",
        text="Fair/Poor", showarrow=False,
        font=dict(size=9, color="#f87171"),
        xanchor="left",
    )

    fig.update_layout(
        title=dict(
            text="7-Day Fishing Quality Forecast",
            font=dict(size=13, color="#f1f1f3"),
        ),
        paper_bgcolor="#111318",
        plot_bgcolor="#111318",
        font=dict(color="#8b8b8f"),
        height=295,
        showlegend=False,
        hovermode="x unified",
        margin=dict(l=0, r=80, t=35, b=55),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color="#8b8b8f"),
            title="",
        ),
        yaxis=dict(
            range=[-20, 110],
            gridcolor="#1e1e20",
            title=dict(text="Score /100", font=dict(size=10)),
            tickfont=dict(color="#8b8b8f"),
        ),
    )

    return fig
