import datetime

_PHASE_EMOJI = {
    "new": "🌑", "waxing_crescent": "🌒", "first_quarter": "🌓",
    "waxing_gibbous": "🌔", "full": "🌕", "waning_gibbous": "🌖",
    "last_quarter": "🌗", "waning_crescent": "🌘",
}

_PHASE_LABEL = {
    "new": "New", "waxing_crescent": "Wax Crescent", "first_quarter": "1st Qtr",
    "waxing_gibbous": "Wax Gibbous", "full": "Full", "waning_gibbous": "Wan Gibbous",
    "last_quarter": "Last Qtr", "waning_crescent": "Wan Crescent",
}


def _score_color(score: int) -> str:
    if score >= 80:
        return "#22c55e"
    if score >= 60:
        return "#fbbf24"
    return "#94a3b8"


def build_moon_strip_html(week_data: list) -> str:
    today = datetime.date.today()
    cards = []
    for d in week_data:
        day_label  = d["date"].strftime("%a")
        is_today   = d["date"] == today
        emoji      = _PHASE_EMOJI.get(d["phase"], "🌙")
        phase_name = _PHASE_LABEL.get(d["phase"], d["phase"].replace("_", " ").title())
        score      = d["score"]
        color      = _score_color(score)
        border     = "border:1.5px solid #38bdf8;" if is_today else "border:1px solid #334155;"
        today_dot  = '<div style="width:5px;height:5px;background:#38bdf8;border-radius:50%;margin:0 auto 2px"></div>' if is_today else ""
        cards.append(
            f'<div style="text-align:center;padding:8px 4px;background:#1e293b;border-radius:8px;flex:1;{border}">'
            f'{today_dot}'
            f'<div style="font-size:11px;color:{"#38bdf8" if is_today else "#64748b"};font-weight:{"600" if is_today else "400"}">{day_label}</div>'
            f'<div style="font-size:26px;line-height:1.3">{emoji}</div>'
            f'<div style="font-size:9px;color:#475569;margin-bottom:2px">{phase_name}</div>'
            f'<div style="font-size:12px;color:{color};font-weight:700">{score}</div>'
            f'</div>'
        )
    score_legend = (
        '<div style="font-size:10px;color:#475569;margin-top:6px">'
        '<span style="color:#22c55e">■</span> 80+ Prime &nbsp;'
        '<span style="color:#fbbf24">■</span> 60+ Good &nbsp;'
        '<span style="color:#94a3b8">■</span> Below 60'
        '</div>'
    )
    return (
        f'<div style="display:flex;gap:6px;margin-bottom:4px">{"".join(cards)}</div>'
        f'{score_legend}'
    )
