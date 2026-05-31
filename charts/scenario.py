import plotly.graph_objects as go

_BASELINE_COLOR  = "#2a2a2e"
_BASELINE_LINE   = "#6b7280"
_ELEVATED_COLOR  = "#f87171"
_UNCHANGED_COLOR = "#4ade80"
_ELEVATION_THRESHOLD = 0.05  # >5% increase → red


def _scenario_bar_colors(baseline: dict, scenario: dict) -> list:
    """Return a list of hex colors for scenario bars, one per category key."""
    colors = []
    for k in baseline:
        b = baseline[k]
        s = scenario.get(k, b)
        if b > 0 and (s - b) / b > _ELEVATION_THRESHOLD:
            colors.append(_ELEVATED_COLOR)
        else:
            colors.append(_UNCHANGED_COLOR)
    return colors


def build_scenario_comparison(
    baseline: dict, scenario: dict, sku_labels: dict, subtitle: str = ""
) -> go.Figure:
    categories = list(baseline.keys())
    labels     = [sku_labels.get(k, k) for k in categories]
    base_vals  = [baseline[k] for k in categories]
    scen_vals  = [scenario.get(k, baseline[k]) for k in categories]
    scen_colors = _scenario_bar_colors(baseline, scenario)

    delta_texts = []
    for b, s in zip(base_vals, scen_vals):
        if b > 0:
            pct = (s - b) / b * 100
            delta_texts.append(f"+{pct:.0f}%" if pct >= 0 else f"{pct:.0f}%")
        else:
            delta_texts.append("—")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Baseline demand",
        x=labels, y=base_vals,
        marker_color=_BASELINE_COLOR,
        marker_line_color=_BASELINE_LINE,
        marker_line_width=1.5,
        hovertemplate="<b>%{x}</b><br>Baseline: %{y:.0f} units/wk<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Scenario",
        x=labels, y=scen_vals,
        marker_color=scen_colors,
        marker_line_color=scen_colors,
        marker_line_width=1.5,
        text=delta_texts,
        textposition="outside",
        textfont=dict(size=11, color="#94a3b8"),
        hovertemplate="<b>%{x}</b><br>Scenario: %{y:.0f} units/wk<br>%{text} vs baseline<extra></extra>",
        showlegend=False,
    ))
    # Invisible dummy traces — give the legend proper color-labeled entries for both scenario states
    fig.add_trace(go.Bar(x=[], y=[], name="Elevated — review stock",
                         marker_color=_ELEVATED_COLOR, showlegend=True))
    fig.add_trace(go.Bar(x=[], y=[], name="Unchanged",
                         marker_color=_UNCHANGED_COLOR, showlegend=True))

    title_text = "Baseline vs Scenario Demand"
    if subtitle:
        title_text += f"  ·  {subtitle}"

    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="#111318",
        plot_bgcolor="#111318",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            font=dict(color="#94a3b8", size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="Units / Week"),
        title=dict(text=title_text, font=dict(color="#94a3b8", size=13)),
        height=320,
        uniformtext=dict(minsize=10, mode="hide"),
    )
    return fig
