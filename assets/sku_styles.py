# Visual identity per SKU category — used in inventory cards and gauges.

SKU_STYLES = {
    "soft_plastics": {
        "gradient": "linear-gradient(135deg, #0c3a5c 0%, #0a4a7a 100%)",
        "accent":   "#38bdf8",
        "label":    "Soft Plastics",
    },
    "hard_baits": {
        "gradient": "linear-gradient(135deg, #1a1745 0%, #27227a 100%)",
        "accent":   "#a78bfa",
        "label":    "Hard Baits",
    },
    "bait": {
        "gradient": "linear-gradient(135deg, #0f3a20 0%, #145228 100%)",
        "accent":   "#4ade80",
        "label":    "Bait",
    },
    "terminal_tackle": {
        "gradient": "linear-gradient(135deg, #1c1917 0%, #292524 100%)",
        "accent":   "#94a3b8",
        "label":    "Terminal Tackle",
    },
    "bucktails_jigs": {
        "gradient": "linear-gradient(135deg, #3a1503 0%, #6a2d0a 100%)",
        "accent":   "#fbbf24",
        "label":    "Bucktails & Jigs",
    },
    "line_leaders": {
        "gradient": "linear-gradient(135deg, #0f1f35 0%, #1a2f4a 100%)",
        "accent":   "#7dd3fc",
        "label":    "Line & Leaders",
    },
    "accessories": {
        "gradient": "linear-gradient(135deg, #111113 0%, #1c1c1e 100%)",
        "accent":   "#64748b",
        "label":    "Accessories",
    },
}

SOURCE_BADGES = {
    "noaa":    {"label": "NOAA CO-OPS",    "color": "#0c2d4a", "text": "#7dd3fc"},
    "ndbc":    {"label": "NDBC Buoy",      "color": "#0c2d4a", "text": "#7dd3fc"},
    "meteo":   {"label": "Open-Meteo",     "color": "#0a2a28", "text": "#5eead4"},
    "reddit":  {"label": "Reddit",         "color": "#2d120a", "text": "#fdba74"},
    "trends":  {"label": "Google Trends",  "color": "#111e30", "text": "#93c5fd"},
    "exa":     {"label": "Exa",            "color": "#200a22", "text": "#f0abfc"},
    "groq":    {"label": "Groq · LLaMA 3", "color": "#0a2010", "text": "#86efac"},
    "seed":    {"label": "Demo Data",      "color": "#1c1c1e", "text": "#8b8b8f"},
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
        "Critical":    "#f87171",
        "Reorder Soon": "#fb923c",
        "Watch":       "#fbbf24",
        "Healthy":     "#4ade80",
    }
    color = colors.get(status, "#8b8b8f")
    pct = min(dos / (lead_time * 3) * 100, 100) if lead_time > 0 else 50
    return (
        f'<div style="background:#111113;border-radius:4px;height:5px;margin:6px 0 2px">'
        f'<div style="background:{color};height:5px;border-radius:4px;width:{pct:.0f}%;'
        f'transition:width 0.3s ease"></div></div>'
        f'<div style="font-size:10px;color:#8b8b8f">{dos:.0f}d supply / {lead_time}d lead time</div>'
    )
