from html import escape


def build_web_report_card(report: dict) -> str:
    title       = escape(report.get("title", "Fishing Report"))
    snippet     = escape(report.get("snippet", ""))
    url         = escape(report.get("url", "#"))
    source      = escape(report.get("source_label", "Web"))
    time_ago    = escape(report.get("time_ago", ""))
    color       = report.get("source_color", "#6b7280")

    body_html = (
        f'<div style="font-size:12px;color:#a1a1aa;line-height:1.6;margin:8px 0 10px">'
        f'{snippet}'
        f'</div>'
    ) if snippet else ""

    return (
        f'<div style="background:#1c1c1e;border:1px solid #2a2a2e;border-left:3px solid {color};'
        f'border-radius:8px;padding:12px 14px;margin-bottom:9px">'

        # Source badge + time
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px">'
        f'<span style="background:rgba(0,0,0,0.3);border:1px solid {color}55;color:{color};'
        f'padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;letter-spacing:0.03em">'
        f'{source}</span>'
        f'<span style="font-size:10px;color:#6b7280">{time_ago}</span>'
        f'</div>'

        # Title (clickable)
        f'<a href="{url}" target="_blank" style="text-decoration:none">'
        f'<div style="font-size:13px;font-weight:600;color:#f1f1f3;line-height:1.4">{title}</div>'
        f'</a>'

        # Snippet
        f'{body_html}'

        # Link
        f'<div style="font-size:10px;color:#6b7280;margin-top:4px">↗ {escape(report.get("domain",""))}</div>'

        f'</div>'
    )


def build_web_report_feed(reports: list, max_items: int = 10) -> str:
    if not reports:
        return (
            '<div style="background:#1c1c1e;border:1px solid #2a2a2e;border-radius:8px;'
            'padding:16px;text-align:center;color:#6b7280;font-size:12px">'
            'No recent web reports — Exa API key required or no results in the last 14 days.</div>'
        )
    return "".join(build_web_report_card(r) for r in reports[:max_items])
