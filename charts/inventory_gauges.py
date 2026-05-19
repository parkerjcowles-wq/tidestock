import plotly.graph_objects as go


def build_gauge(
    label: str, value: float, max_val: float, unit: str, rop: float = None
) -> go.Figure:
    pct   = min(value / max_val, 1.0) if max_val > 0 else 0
    color = "#22c55e" if pct > 0.5 else "#fbbf24" if pct > 0.25 else "#ef4444"

    gauge_cfg = {
        "axis": {"range": [0, max_val], "tickcolor": "#475569", "tickfont": {"size": 9}},
        "bar": {"color": color},
        "bgcolor": "#1e293b",
        "bordercolor": "#334155",
        "steps": [
            {"range": [0, max_val * 0.25], "color": "#450a0a"},
            {"range": [max_val * 0.25, max_val * 0.5], "color": "#1c1917"},
            {"range": [max_val * 0.5, max_val], "color": "#0f2417"},
        ],
    }
    if rop is not None and rop <= max_val:
        gauge_cfg["threshold"] = {
            "line": {"color": "#f97316", "width": 2},
            "thickness": 0.75,
            "value": rop,
        }

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": f" {unit}", "font": {"color": color, "size": 18}},
        gauge=gauge_cfg,
        title={"text": label, "font": {"color": "#94a3b8", "size": 12}},
    ))
    fig.update_layout(
        paper_bgcolor="#0f172a", height=185,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig
