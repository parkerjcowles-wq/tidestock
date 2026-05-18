import plotly.graph_objects as go


def build_scenario_comparison(baseline: dict, scenario: dict, sku_labels: dict) -> go.Figure:
    categories = list(baseline.keys())
    labels = [sku_labels.get(k, k) for k in categories]
    base_vals = [baseline[k] for k in categories]
    scen_vals = [scenario.get(k, baseline[k]) for k in categories]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Baseline",
        x=labels, y=base_vals,
        marker_color="#38bdf8",
        hovertemplate="%{x}: %{y:.0f} units/week<extra>Baseline</extra>",
    ))
    fig.add_trace(go.Bar(
        name="Scenario",
        x=labels, y=scen_vals,
        marker_color="#f97316",
        hovertemplate="%{x}: %{y:.0f} units/week<extra>Scenario</extra>",
    ))
    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#94a3b8")),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="Units / Week"),
        title=dict(text="Baseline vs Scenario Demand", font=dict(color="#94a3b8", size=13)),
        height=320,
    )
    return fig
