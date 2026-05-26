import pytest
from ai.brief import build_brief_prompt


def _base_conditions():
    return {
        "date": "2026-05-25",
        "moon_phase": "waxing_gibbous",
        "tide_quality": "moderate",
        "pressure_trend": "stable",
        "water_temp": 57.0,
        "fishing_score": 62,
        "species": {"Striped Bass": "Peak", "Flounder": "Fair"},
    }


def _base_inv():
    return {"Live Bait": {"dos": 2, "urgency": "Order Today", "critical_skus": 1}}


def test_prompt_includes_social_intelligence_block_when_posts_given():
    """SOCIAL INTELLIGENCE block appears when posts are provided."""
    posts = [{
        "title": "Bucktails getting absolutely slammed by stripers at PI mouth",
        "subreddit": "surf_fishing",
        "bait_mentions": ["bucktail"],
        "sentiment": "catching",
        "time_ago": "3h ago",
    }]
    prompt = build_brief_prompt(
        conditions=_base_conditions(),
        inventory_summary=_base_inv(),
        social_velocity="elevated",
        trend_alerts=[],
        tournaments=[],
        social_posts=posts,
    )
    assert "SOCIAL INTELLIGENCE" in prompt
    assert "surf_fishing" in prompt
    assert "Bucktails getting absolutely slammed" in prompt
    assert "bucktail" in prompt


def test_prompt_omits_social_intelligence_block_when_no_posts():
    """SOCIAL INTELLIGENCE block is absent when social_posts is None."""
    prompt = build_brief_prompt(
        conditions=_base_conditions(),
        inventory_summary=_base_inv(),
        social_velocity="baseline",
        trend_alerts=[],
        tournaments=[],
        social_posts=None,
    )
    assert "SOCIAL INTELLIGENCE" not in prompt


def test_prompt_omits_social_intelligence_block_when_empty_list():
    """SOCIAL INTELLIGENCE block is absent when social_posts is empty."""
    prompt = build_brief_prompt(
        conditions=_base_conditions(),
        inventory_summary=_base_inv(),
        social_velocity="baseline",
        trend_alerts=[],
        tournaments=[],
        social_posts=[],
    )
    assert "SOCIAL INTELLIGENCE" not in prompt


def test_prompt_includes_web_reports_when_given():
    """Web report headlines appear in prompt when web_reports provided."""
    reports = [{
        "source_label": "On The Water",
        "title": "Plum Island striper action strong — bloodworms and paddle tails working",
        "time_ago": "2d ago",
    }]
    prompt = build_brief_prompt(
        conditions=_base_conditions(),
        inventory_summary=_base_inv(),
        social_velocity="baseline",
        trend_alerts=[],
        tournaments=[],
        web_reports=reports,
    )
    assert "On The Water" in prompt
    assert "Plum Island striper action strong" in prompt


def test_prompt_includes_citation_instruction():
    """Dave's instruction to cite sources appears when posts are passed."""
    posts = [{
        "title": "Paddle tails on fire this week",
        "subreddit": "SaltwaterFishing",
        "bait_mentions": ["paddle tail"],
        "sentiment": "catching",
        "time_ago": "1h ago",
    }]
    prompt = build_brief_prompt(
        conditions=_base_conditions(),
        inventory_summary=_base_inv(),
        social_velocity="elevated",
        trend_alerts=[],
        tournaments=[],
        social_posts=posts,
    )
    assert "cite" in prompt.lower() or "quote" in prompt.lower()


def test_prompt_caps_posts_at_four():
    """Only the first 4 posts appear even if more are passed."""
    posts = [
        {"title": f"Post {i}", "subreddit": "surf_fishing",
         "bait_mentions": ["bucktail"], "sentiment": "catching", "time_ago": f"{i}h ago"}
        for i in range(6)
    ]
    prompt = build_brief_prompt(
        conditions=_base_conditions(),
        inventory_summary=_base_inv(),
        social_velocity="elevated",
        trend_alerts=[],
        tournaments=[],
        social_posts=posts,
    )
    assert prompt.count("surf_fishing") <= 4
