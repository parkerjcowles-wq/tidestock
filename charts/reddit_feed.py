from html import escape

_SENTIMENT_STYLE = {
    "catching": {"bg": "#052e16", "border": "#166534", "badge_bg": "#14532d", "badge_color": "#4ade80", "label": "Catching"},
    "slow":     {"bg": "#1c1c1e", "border": "#2a2a2e", "badge_bg": "#2a2a2e", "badge_color": "#6b7280", "label": "Slow"},
    "neutral":  {"bg": "#1c1c1e", "border": "#2a2a2e", "badge_bg": "#1e3a5f", "badge_color": "#93c5fd", "label": "Conditions"},
}

_CATEGORY_LABELS = {
    "soft_plastics":  "Soft Plastics",
    "hard_baits":     "Hard Baits",
    "bait":           "Live Bait",
    "terminal_tackle": "Terminal Tackle",
    "bucktails_jigs": "Bucktails & Jigs",
    "line_leaders":   "Line & Leaders",
    "accessories":    "Accessories",
}

_CATEGORY_COLORS = {
    "soft_plastics":  "#a78bfa",
    "hard_baits":     "#60a5fa",
    "bait":           "#f97316",
    "terminal_tackle": "#fbbf24",
    "bucktails_jigs": "#34d399",
    "line_leaders":   "#94a3b8",
    "accessories":    "#f472b6",
}


def _keyword_chip(kw: str) -> str:
    return (
        f'<span style="background:#1e3a5f;color:#93c5fd;padding:2px 8px;'
        f'border-radius:12px;font-size:10px;white-space:nowrap">'
        f'{escape(kw)}</span>'
    )


def _sku_impact_chip(cat: str) -> str:
    label = _CATEGORY_LABELS.get(cat, cat)
    color = _CATEGORY_COLORS.get(cat, "#94a3b8")
    return (
        f'<span style="background:#111113;border:1px solid {color};color:{color};'
        f'padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600;'
        f'white-space:nowrap">↑ {escape(label)}</span>'
    )


def build_post_card_html(post: dict) -> str:
    s = _SENTIMENT_STYLE.get(post.get("sentiment", "neutral"), _SENTIMENT_STYLE["neutral"])

    title   = escape(post["title"][:100]) + ("…" if len(post["title"]) > 100 else "")
    body    = escape(post.get("body", ""))
    author  = escape(post.get("author", "angler"))
    sub     = escape(post.get("subreddit", "fishing"))
    t_ago   = escape(post.get("time_ago", ""))
    url     = escape(post.get("url", "#"))
    upvotes = post.get("upvotes", 0)
    comments = post.get("comments", 0)
    initials = escape(post.get("initials", "??"))
    av_color = post.get("avatar_color", "#1d4ed8")

    badge = (
        f'<span style="background:{s["badge_bg"]};color:{s["badge_color"]};'
        f'padding:3px 9px;border-radius:4px;font-size:11px;font-weight:600">'
        f'{s["label"]}</span>'
    )

    kw_chips = " ".join(_keyword_chip(kw) for kw in post.get("bait_mentions", [])[:4])
    sku_chips = " ".join(_sku_impact_chip(c) for c in post.get("category_signals", [])[:3])

    body_html = (
        f'<div style="font-size:12px;color:#a1a1aa;line-height:1.6;margin:8px 0;'
        f'max-height:42px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical">'
        f'{body}'
        f'</div>'
    ) if body else ""

    sku_row = (
        f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px;'
        f'padding-top:10px;border-top:1px solid #2a2a2e;align-items:center">'
        f'<span style="font-size:10px;color:#6b7280;margin-right:2px">Inventory impact →</span>'
        f'{sku_chips}'
        f'</div>'
    ) if sku_chips else ""

    kw_row = (
        f'<div style="display:flex;gap:5px;flex-wrap:wrap;margin-top:8px">'
        f'{kw_chips}'
        f'</div>'
    ) if kw_chips else ""

    return (
        f'<div style="background:{s["bg"]};border:1px solid {s["border"]};'
        f'border-radius:10px;padding:14px 16px;margin-bottom:10px">'

        # Header row: avatar + meta + sentiment badge
        f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px">'
        f'<div style="width:36px;height:36px;border-radius:50%;background:{av_color};'
        f'flex-shrink:0;display:flex;align-items:center;justify-content:center;'
        f'font-size:13px;font-weight:700;color:#fff">{initials}</div>'
        f'<div style="flex:1;min-width:0">'
        f'<div style="font-size:13px;font-weight:600;color:#f1f1f3">u/{author}</div>'
        f'<div style="font-size:11px;color:#6b7280">r/{sub} · {t_ago}</div>'
        f'</div>'
        f'<div style="flex-shrink:0">{badge}</div>'
        f'</div>'

        # Title
        f'<a href="{url}" style="text-decoration:none">'
        f'<div style="font-size:14px;font-weight:600;color:#f1f1f3;line-height:1.4">'
        f'{title}</div>'
        f'</a>'

        # Body
        f'{body_html}'

        # Keyword chips
        f'{kw_row}'

        # Engagement
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px">'
        f'<span style="font-size:11px;color:#6b7280">▲ {upvotes} · {comments} comments</span>'
        f'</div>'

        # SKU impact
        f'{sku_row}'

        f'</div>'
    )


def build_reddit_feed_html(posts: list, max_posts: int = 6) -> str:
    if not posts:
        return (
            '<div style="background:#1c1c1e;border:1px solid #2a2a2e;border-radius:8px;'
            'padding:20px;text-align:center;color:#6b7280;font-size:13px">'
            'No qualifying Reddit signals in the current fetch window.</div>'
        )
    return "".join(build_post_card_html(p) for p in posts[:max_posts])


def build_catch_intel_cards(posts: list, max_posts: int = 3) -> str:
    """Compact version for Command Center — catching posts only, with SKU impact."""
    catching = [p for p in posts if p.get("sentiment") == "catching" and p.get("category_signals")]
    if not catching:
        return ""
    cards = []
    for p in catching[:max_posts]:
        author  = escape(p.get("author", "angler"))
        sub     = escape(p.get("subreddit", "fishing"))
        t_ago   = escape(p.get("time_ago", ""))
        title   = escape(p["title"])[:80] + ("…" if len(p["title"]) > 80 else "")
        url     = escape(p.get("url", "#"))
        av_color = p.get("avatar_color", "#1d4ed8")
        initials = escape(p.get("initials", "??"))
        sku_chips = " ".join(_sku_impact_chip(c) for c in p.get("category_signals", [])[:3])
        kw_chips  = " ".join(_keyword_chip(kw) for kw in p.get("bait_mentions", [])[:3])

        cards.append(
            f'<div style="background:#052e16;border:1px solid #166534;border-radius:8px;'
            f'padding:12px 14px;margin-bottom:8px">'

            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">'
            f'<div style="width:28px;height:28px;border-radius:50%;background:{av_color};'
            f'flex-shrink:0;display:flex;align-items:center;justify-content:center;'
            f'font-size:11px;font-weight:700;color:#fff">{initials}</div>'
            f'<div>'
            f'<span style="font-size:12px;font-weight:600;color:#f1f1f3">u/{author}</span>'
            f'<span style="font-size:11px;color:#6b7280"> · r/{sub} · {t_ago}</span>'
            f'</div>'
            f'<span style="margin-left:auto;font-size:11px;font-weight:600;color:#4ade80">Catching</span>'
            f'</div>'

            f'<a href="{url}" style="text-decoration:none">'
            f'<div style="font-size:13px;color:#d1fae5;line-height:1.4;margin-bottom:8px">{title}</div>'
            f'</a>'

            f'<div style="display:flex;gap:5px;flex-wrap:wrap;margin-bottom:8px">{kw_chips}</div>'

            f'<div style="display:flex;gap:5px;flex-wrap:wrap;align-items:center">'
            f'<span style="font-size:10px;color:#6b7280">Demand →</span>{sku_chips}'
            f'</div>'

            f'</div>'
        )
    return "".join(cards)
