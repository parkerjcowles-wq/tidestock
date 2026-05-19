import plotly.graph_objects as go


def build_scenario_comparison(
    baseline: dict, scenario: dict, sku_labels: dict, subtitle: str = ""
) -> go.Figure:
    categories = list(baseline.keys())
    labels     = [sku_labels.get(k, k) for k in categories]
    base_vals  = [baseline[k] for k in categories]
    scen_vals  = [scenario.get(k, baseline[k]) for k in categories]

    delta_texts = []
    for b, s in zip(base_vals, scen_vals):
        if b > 0:
            pct = (s - b) / b * 100
            delta_texts.append(f"+{pct:.0f}%" if pct >= 0 else f"{pct:.0f}%")
        else:
            delta_texts.append("—")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Baseline",
        x=labels, y=base_vals,
        marker_color="#38bdf8",
        hovertemplate="<b>%{x}</b><br>Baseline: %{y:.0f} units/wk<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Scenario",
        x=labels, y=scen_vals,
        marker_color="#f97316",
        text=delta_texts,
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="<b>%{x}</b><br>Scenario: %{y:.0f} units/wk<extra></extra>",
    ))

    title_text = "Baseline vs Scenario Demand"
    if subtitle:
        title_text += f"  ·  {subtitle}"

    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#94a3b8")),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="Units / Week"),
        title=dict(text=title_text, font=dict(color="#94a3b8", size=13)),
        height=320,
        uniformtext=dict(minsize=10, mode="hide"),
    )
    return fig
