import requests
import config

_HEADERS = {"User-Agent": "TideStock/1.0 (portfolio project; read-only public data)"}


def extract_bait_mentions(text: str, keywords: list) -> list:
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def classify_velocity(upvotes: int, comments: int) -> str:
    if upvotes >= 300 or comments >= 50:
        return "trending"
    if upvotes >= 100 or comments >= 15:
        return "elevated"
    return "baseline"


def fetch_reddit_signals(limit: int = 10) -> list:
    posts = []
    for sub_name in config.REDDIT_SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{sub_name}/new.json?limit={limit}"
            resp = requests.get(url, headers=_HEADERS, timeout=10)
            resp.raise_for_status()
            children = resp.json()["data"]["children"]
            for child in children:
                d = child["data"]
                mentions = extract_bait_mentions(
                    f"{d['title']} {d.get('selftext', '')}", config.FISHING_KEYWORDS
                )
                velocity = classify_velocity(d["score"], d["num_comments"])
                posts.append({
                    "title": d["title"],
                    "subreddit": sub_name,
                    "upvotes": d["score"],
                    "comments": d["num_comments"],
                    "url": f"https://reddit.com{d['permalink']}",
                    "bait_mentions": mentions,
                    "velocity": velocity,
                })
        except Exception:
            continue
    posts.sort(key=lambda x: x["upvotes"], reverse=True)
    return posts[:15]


def get_overall_social_velocity(posts: list) -> str:
    if not posts:
        return "baseline"
    trending = sum(1 for p in posts if p["velocity"] == "trending")
    elevated = sum(1 for p in posts if p["velocity"] == "elevated")
    if trending >= 2:
        return "trending"
    if trending >= 1 or elevated >= 3:
        return "elevated"
    return "baseline"
