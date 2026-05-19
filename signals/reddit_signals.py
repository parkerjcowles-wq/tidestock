import os
import praw
import config


def get_reddit_client() -> praw.Reddit:
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise EnvironmentError("Reddit credentials not configured")
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=os.environ.get("REDDIT_USER_AGENT", "TideStock/1.0"),
    )


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
    reddit = get_reddit_client()
    posts = []
    for sub_name in config.REDDIT_SUBREDDITS:
        sub = reddit.subreddit(sub_name)
        for post in sub.new(limit=limit):
            mentions = extract_bait_mentions(
                f"{post.title} {post.selftext}", config.FISHING_KEYWORDS
            )
            velocity = classify_velocity(post.score, post.num_comments)
            posts.append({
                "title": post.title,
                "subreddit": sub_name,
                "upvotes": post.score,
                "comments": post.num_comments,
                "url": f"https://reddit.com{post.permalink}",
                "bait_mentions": mentions,
                "velocity": velocity,
            })
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
