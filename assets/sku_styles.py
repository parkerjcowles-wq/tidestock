# Visual identity for each SKU category — used in inventory cards and gauges.
# Gradients are CSS linear-gradient strings; accent is the highlight color.

SKU_STYLES = {
    "soft_plastics": {
        "gradient": "linear-gradient(135deg, #0c4a6e 0%, #075985 100%)",
        "accent":   "#38bdf8",
        "icon":     "🪱",
        "label":    "Soft Plastics",
    },
    "hard_baits": {
        "gradient": "linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)",
        "accent":   "#a78bfa",
        "icon":     "🎣",
        "label":    "Hard Baits",
    },
    "live_bait": {
        "gradient": "linear-gradient(135deg, #14532d 0%, #166534 100%)",
        "accent":   "#4ade80",
        "icon":     "🐛",
        "label":    "Live Bait",
    },
    "terminal_tackle": {
        "gradient": "linear-gradient(135deg, #1c1917 0%, #292524 100%)",
        "accent":   "#94a3b8",
        "icon":     "🪝",
        "label":    "Terminal Tackle",
    },
    "bucktails_jigs": {
        "gradient": "linear-gradient(135deg, #451a03 0%, #78350f 100%)",
        "accent":   "#fbbf24",
        "icon":     "🪶",
        "label":    "Bucktails & Jigs",
    },
    "accessories": {
        "gradient": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        "accent":   "#64748b",
        "icon":     "🧰",
        "label":    "Accessories",
    },
}

# Source badges shown on data panels
SOURCE_BADGES = {
    "noaa":    {"label": "NOAA CO-OPS",    "color": "#0369a1", "text": "#7dd3fc"},
    "ndbc":    {"label": "NDBC Buoy",      "color": "#0369a1", "text": "#7dd3fc"},
    "meteo":   {"label": "Open-Meteo",     "color": "#0f766e", "text": "#5eead4"},
    "reddit":  {"label": "Reddit",         "color": "#7c2d12", "text": "#fdba74"},
    "trends":  {"label": "Google Trends",  "color": "#1e3a5f", "text": "#93c5fd"},
    "exa":     {"label": "Exa",            "color": "#4a044e", "text": "#f0abfc"},
    "groq":    {"label": "Groq · LLaMA 3", "color": "#14532d", "text": "#86efac"},
    "seed":    {"label": "Demo Data",      "color": "#1e293b", "text": "#94a3b8"},
}


def source_badge_html(key: str, last_updated: str = "") -> str:
    b = SOURCE_BADGES.get(key, SOURCE_BADGES["seed"])
    ts = f' · <span style="opacity:0.7">{last_updated}</span>' if last_updated else ""
    return (
        f'<span style="background:{b["color"]};color:{b["text"]};'
        f'padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600;'
        f'font-family:monospace">{b["label"]}{ts}</span>'
    )


def dos_progress_bar_html(dos: float, lead_time: int, status: str) -> str:
    colors = {
        "🔴 Critical":    "#ef4444",
        "🟠 Reorder Soon": "#f97316",
        "🟡 Watch":        "#fbbf24",
        "🟢 Healthy":      "#22c55e",
    }
    color = colors.get(status, "#94a3b8")
    # Fill relative to 3× lead time = "full" bucket
    pct = min(dos / (lead_time * 3) * 100, 100) if lead_time > 0 else 50
    return (
        f'<div style="background:#0f172a;border-radius:4px;height:5px;margin:6px 0 2px">'
        f'<div style="background:{color};height:5px;border-radius:4px;width:{pct:.0f}%;'
        f'transition:width 0.3s ease"></div></div>'
        f'<div style="font-size:10px;color:#475569">{dos:.0f}d supply / {lead_time}d lead time</div>'
    )
