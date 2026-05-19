import plotly.graph_objects as go

_URGENCY_COLOR = {
    "🔴 Critical": "#ef4444",
    "🟠 Reorder Soon": "#f97316",
    "🟡 Watch": "#fbbf24",
    "🟢 Healthy": "#22c55e",
}


def build_dos_chart(dos_data: list) -> go.Figure:
    dos_data_sorted = sorted(dos_data, key=lambda x: x["dos"])
    labels = [d["label"] for d in dos_data_sorted]
    values = [d["dos"] for d in dos_data_sorted]
    colors = [_URGENCY_COLOR.get(d["urgency"], "#94a3b8") for d in dos_data_sorted]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=colors),
        hovertemplate="%{y}: %{x:.0f} days<extra></extra>",
    ))
    fig.add_vline(x=7, line=dict(color="#ef4444", dash="dash", width=1),
                  annotation_text="1 Week Supply", annotation_font_color="#ef4444")
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        margin=dict(l=10, r=10, t=30, b=10), height=280,
        xaxis=dict(title="Days of Supply", showgrid=True, gridcolor="#1e293b"),
        yaxis=dict(showgrid=False),
        title=dict(text="Days of Supply by Category", font=dict(color="#94a3b8", size=13)),
    )
    return fig
