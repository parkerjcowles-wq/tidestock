import plotly.graph_objects as go


def build_gauge(
    label: str, value: float, max_val: float, unit: str, rop: float = None
) -> go.Figure:
    pct   = min(value / max_val, 1.0) if max_val > 0 else 0
    color = "#4ade80" if pct > 0.5 else "#fbbf24" if pct > 0.25 else "#f87171"

    gauge_cfg = {
        "axis": {"range": [0, max_val], "tickcolor": "#2a2a2e", "tickfont": {"size": 9, "color": "#8b8b8f"}},
        "bar": {"color": color},
        "bgcolor": "#2a2a2e",
        "bordercolor": "#3a3a3e",
        "steps": [
            {"range": [0, max_val * 0.25], "color": "#2d0f0f"},
            {"range": [max_val * 0.25, max_val * 0.5], "color": "#261600"},
            {"range": [max_val * 0.5, max_val], "color": "#0a1f0f"},
        ],
    }
    if rop is not None and rop <= max_val:
        gauge_cfg["threshold"] = {
            "line": {"color": "#fb923c", "width": 2},
            "thickness": 0.75,
            "value": rop,
        }

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": f" {unit}", "font": {"color": color, "size": 12}},
        gauge=gauge_cfg,
        title={"text": label, "font": {"color": "#c8c8cc", "size": 11}},
    ))
    fig.update_layout(
        paper_bgcolor="#1c1c1e", height=180,
        margin=dict(l=18, r=18, t=42, b=8),
    )
    return fig
