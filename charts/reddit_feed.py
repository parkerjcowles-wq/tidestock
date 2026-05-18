_VELOCITY_STYLE = {
    "trending": ("🔴", "#450a0a", "#fca5a5"),
    "elevated": ("🟡", "#422006", "#fde68a"),
    "baseline": ("⚪", "#1e293b", "#94a3b8"),
}


def build_reddit_card_html(post: dict) -> str:
    icon, bg, text_color = _VELOCITY_STYLE.get(post["velocity"], _VELOCITY_STYLE["baseline"])
    mentions_html = " ".join(
        f'<span style="background:#0f4c81;color:#93c5fd;padding:2px 8px;border-radius:12px;font-size:11px">{m}</span>'
        for m in post["bait_mentions"]
    ) or '<span style="color:#475569;font-size:11px">no keywords</span>'
    return (
        f'<div style="background:{bg};border-radius:10px;padding:12px 16px;margin-bottom:8px">'
        f'<div style="display:flex;justify-content:space-between;align-items:center">'
        f'<span style="font-size:11px;color:#64748b">r/{post["subreddit"]}</span>'
        f'<span style="font-size:11px">{icon} {post["velocity"]}</span></div>'
        f'<div style="color:{text_color};font-size:13px;margin:6px 0">'
        f'<a href="{post["url"]}" style="color:{text_color};text-decoration:none">'
        f'{post["title"][:90]}{"…" if len(post["title"]) > 90 else ""}</a></div>'
        f'<div style="display:flex;gap:12px;align-items:center">'
        f'<span style="color:#64748b;font-size:11px">▲ {post["upvotes"]} · 💬 {post["comments"]}</span>'
        f'<div>{mentions_html}</div></div></div>'
    )


def build_reddit_feed_html(posts: list) -> str:
    if not posts:
        return '<div style="color:#475569;padding:16px">No recent posts found.</div>'
    return "".join(build_reddit_card_html(p) for p in posts[:5])
