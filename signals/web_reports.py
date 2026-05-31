import os
import time
import datetime
import requests
import config

_EXA_URL = "https://api.exa.ai/search"

_DOMAIN_LABELS = {
    "onthewater.com":       "On The Water",
    "thefisherman.com":     "The Fisherman",
    "stripersonline.com":   "StripersOnline",
    "myfishingcapecod.com": "My Fishing Cape Cod",
    "ristripedbass.blogspot.com": "RI Striper Bass",
    "blogspot.com":         "Fishing Blog",
    "reddit.com":           "Reddit",
    "youtube.com":          "YouTube",
    "instagram.com":        "Instagram",
    "fishcrusade.com":      "Fish Crusade",
    "dsflyfishing.com":     "DS Fly Fishing",
}

_DOMAIN_COLORS = {
    "onthewater.com":       "#0ea5e9",
    "thefisherman.com":     "#f59e0b",
    "stripersonline.com":   "#22c55e",
    "myfishingcapecod.com": "#a78bfa",
    "reddit.com":           "#f97316",
    "default":              "#6b7280",
}

_QUERIES = [
    f"Plum Island Newburyport striper fishing report {datetime.date.today().strftime('%B %Y')}",
    f"Massachusetts New England fishing report striper {datetime.date.today().strftime('%B %Y')}",
    f"striper migration report Cape Ann North Shore {datetime.date.today().strftime('%B %Y')}",
]


def _domain_from_url(url: str) -> str:
    try:
        host = url.split("/")[2].lower()
        return host.removeprefix("www.")
    except Exception:
        return "web"


def _label_for_domain(domain: str) -> str:
    for key, label in _DOMAIN_LABELS.items():
        if key in domain:
            return label
    # Fall back to cleaned domain name
    parts = domain.split(".")
    return parts[-2].replace("-", " ").title() if len(parts) >= 2 else domain


def _color_for_domain(domain: str) -> str:
    for key, color in _DOMAIN_COLORS.items():
        if key in domain:
            return color
    return _DOMAIN_COLORS["default"]


def _format_date(iso_str: str) -> str:
    if not iso_str:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        diff = now - dt
        if diff.days == 0:
            return "Today"
        if diff.days == 1:
            return "Yesterday"
        if diff.days <= 14:
            return f"{diff.days}d ago"
        return dt.strftime("%b %d")
    except Exception:
        return ""


def _is_relevant(title: str, text: str) -> bool:
    """Filter out results that are clearly not fishing reports."""
    combined = (title + " " + (text or "")).lower()
    skip_terms = ["javascript", "cookie policy", "subscribe", "newsletter", "!function",
                   "skip to main content", "table of contents", "log in", "day pass",
                   "subscriber login", "sign up for free"]
    if any(t in combined[:200] for t in skip_terms):
        return False
    fish_terms = ["fish", "striper", "bass", "flounder", "bait", "catch", "rod", "reel",
                  "tide", "surf", "angler", "tackle", "hook", "lure"]
    return any(t in combined for t in fish_terms)


def fetch_web_fishing_reports(days: int = 14) -> list:
    """Pull fishing reports from across the web via Exa neural search."""
    api_key = os.environ.get("EXA_API_KEY", "")
    if not api_key:
        return []

    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    seen_urls: set = set()
    reports = []

    for query in _QUERIES:
        try:
            resp = requests.post(
                _EXA_URL,
                headers={"x-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "query": query,
                    "numResults": 8,
                    "useAutoprompt": True,
                    "type": "neural",
                    "startPublishedDate": cutoff,
                    "contents": {"text": {"maxCharacters": 300}},
                },
                timeout=12,
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            for res in results:
                url = res.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                title = (res.get("title") or "").strip()
                text  = (res.get("text") or "").strip()
                if not _is_relevant(title, text):
                    continue
                domain = _domain_from_url(url)
                snippet = text[:260].replace("#", "").replace("[![", "").replace("*", "").strip()
                _chrome = ["Skip to main content", "Table of Contents", "Subscribe",
                           "LOG IN", "Log in", "Day Pass", "Subscriber login",
                           "Channel:", "Length:", "Views:", "Keywords:"]
                for phrase in _chrome:
                    snippet = snippet.replace(phrase, "").strip()
                snippet = " ".join(snippet.split())
                if snippet and "…" not in snippet and len(text) > 260:
                    snippet += "…"
                reports.append({
                    "title":        title[:90] + ("…" if len(title) > 90 else ""),
                    "snippet":      snippet,
                    "url":          url,
                    "domain":       domain,
                    "source_label": _label_for_domain(domain),
                    "source_color": _color_for_domain(domain),
                    "published":    res.get("publishedDate", ""),
                    "time_ago":     _format_date(res.get("publishedDate", "")),
                })
        except Exception:
            continue

    # Sort by most recent, deduplicated
    def _pub_sort_key(r):
        try:
            return datetime.datetime.fromisoformat(r["published"].replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0.0

    reports.sort(key=_pub_sort_key, reverse=True)
    return reports[:18]
