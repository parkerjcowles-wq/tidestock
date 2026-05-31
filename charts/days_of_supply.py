import plotly.graph_objects as go

_URGENCY_COLOR = {
    "Critical":     "#f87171",
    "Reorder Soon": "#fb923c",
    "Watch":        "#fbbf24",
    "Healthy":      "#4ade80",
}


def build_dos_chart(dos_data: list, lead_time_days: int = 5) -> go.Figure:
    dos_data_sorted = sorted(dos_data, key=lambda x: x["dos"])
    labels = [d["label"] for d in dos_data_sorted]
    values = [d["dos"] for d in dos_data_sorted]
    colors = [_URGENCY_COLOR.get(d["urgency"], "#8b8b8f") for d in dos_data_sorted]

    hover = [
        f"<b>{d['label']}</b><br>"
        f"Days of Supply: <b>{d['dos']:.0f}d</b><br>"
        f"Status: {d['urgency']}<br>"
        f"<span style='color:#8b8b8f'>Avg lead time: {lead_time_days}d</span>"
        f"<extra></extra>"
        for d in dos_data_sorted
    ]

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=colors),
        hovertemplate=hover,
    ))

    fig.add_vline(
        x=lead_time_days,
        line=dict(color="#fb923c", dash="dash", width=1.5),
        annotation_text=f"Lead Time ({lead_time_days}d)",
        annotation_font_color="#fb923c",
        annotation_font_size=10,
        annotation_position="top right",
    )
    fig.add_vline(
        x=lead_time_days * 2,
        line=dict(color="#fbbf24", dash="dot", width=1),
        annotation_text="2× Lead Time",
        annotation_font_color="#fbbf24",
        annotation_font_size=10,
        annotation_position="top right",
    )

    fig.update_layout(
        paper_bgcolor="#1c1c1e", plot_bgcolor="#1c1c1e",
        margin=dict(l=10, r=10, t=40, b=10),
        height=max(260, 40 + len(dos_data_sorted) * 22),
        xaxis=dict(
            title="Days of Supply",
            showgrid=True, gridcolor="#2a2a2e",
            tickfont=dict(color="#8b8b8f", size=10),
        ),
        yaxis=dict(showgrid=False, tickfont=dict(color="#f1f1f3", size=10)),
        title=dict(
            text="Days of Supply by SKU — orange line = avg supplier lead time",
            font=dict(color="#8b8b8f", size=12),
        ),
    )
    return fig
