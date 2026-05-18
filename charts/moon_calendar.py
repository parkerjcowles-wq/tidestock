_PHASE_EMOJI = {
    "new": "🌑", "waxing_crescent": "🌒", "first_quarter": "🌓",
    "waxing_gibbous": "🌔", "full": "🌕", "waning_gibbous": "🌖",
    "last_quarter": "🌗", "waning_crescent": "🌘",
}


def _score_color(score: int) -> str:
    if score >= 80:
        return "#22c55e"
    if score >= 60:
        return "#fbbf24"
    return "#94a3b8"


def build_moon_strip_html(week_data: list) -> str:
    cards = []
    for d in week_data:
        day_label = d["date"].strftime("%a")
        emoji = _PHASE_EMOJI.get(d["phase"], "🌙")
        score = d["score"]
        color = _score_color(score)
        cards.append(
            f'<div style="text-align:center;padding:8px;background:#1e293b;border-radius:8px;flex:1">'
            f'<div style="font-size:11px;color:#64748b">{day_label}</div>'
            f'<div style="font-size:24px">{emoji}</div>'
            f'<div style="font-size:12px;color:{color};font-weight:600">{score}</div>'
            f'</div>'
        )
    return f'<div style="display:flex;gap:6px;margin-bottom:12px">{"".join(cards)}</div>'
