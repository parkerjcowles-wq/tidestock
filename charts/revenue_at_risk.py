import plotly.graph_objects as go

_STATUS_COLOR = {
    "Critical":     "#f87171",
    "Reorder Soon": "#fb923c",
    "Watch":        "#fbbf24",
    "Healthy":      "#4ade80",
}


def build_revenue_at_risk_chart(recs: list) -> go.Figure:
    filtered = [r for r in recs if r["rev_risk"] > 0]
    filtered.sort(key=lambda r: r["rev_risk"], reverse=True)

    fig = go.Figure()

    if not filtered:
        fig.add_annotation(
            text="No revenue at risk — all SKUs above reorder point",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color="#8b8b8f", size=13),
        )
        fig.update_layout(
            paper_bgcolor="#1c1c1e", plot_bgcolor="#1c1c1e",
            height=180, margin=dict(l=10, r=10, t=40, b=10),
            title=dict(text="Revenue at Risk by SKU", font=dict(color="#8b8b8f", size=12)),
        )
        return fig

    labels = [r["product_name"] for r in filtered]
    values = [r["rev_risk"] for r in filtered]
    colors = [_STATUS_COLOR.get(r["status"], "#8b8b8f") for r in filtered]
    texts  = [f"${v:,.0f}" for v in values]
    total  = sum(values)

    hover = [
        f"<b>{r['product_name']}</b><br>"
        f"Revenue at Risk: <b>${r['rev_risk']:,.0f}</b><br>"
        f"Status: {r['status']}<br>"
        f"<span style='color:#8b8b8f'>= (ROP − on-hand) × retail price</span>"
        f"<extra></extra>"
        for r in filtered
    ]

    fig.add_trace(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=colors, opacity=0.85),
        text=texts,
        textposition="outside",
        textfont=dict(size=11, color="#f1f1f3"),
        hovertemplate=hover,
    ))

    fig.add_annotation(
        text=f"Total at risk: <b>${total:,.0f}</b>",
        xref="paper", yref="paper", x=1.0, y=1.08,
        showarrow=False,
        font=dict(color="#fb923c", size=12),
        align="right",
    )

    fig.update_layout(
        paper_bgcolor="#1c1c1e", plot_bgcolor="#1c1c1e",
        margin=dict(l=10, r=80, t=50, b=10),
        height=max(200, 50 + len(filtered) * 32),
        xaxis=dict(
            title="$ at Risk",
            showgrid=True, gridcolor="#2a2a2e",
            tickprefix="$", tickfont=dict(color="#8b8b8f", size=10),
        ),
        yaxis=dict(showgrid=False, tickfont=dict(color="#f1f1f3", size=11)),
        title=dict(
            text="Revenue at Risk by SKU — (ROP − on-hand) × retail price",
            font=dict(color="#8b8b8f", size=12),
        ),
    )
    return fig
