from signals.web_reports import _clean_snippet, _title_is_useful, _is_relevant
from charts.web_report_feed import build_web_report_feed
from charts.reddit_feed import build_reddit_feed_html


# ── Snippet cleaning ──────────────────────────────────────────────────────────

def test_clean_snippet_hides_pure_chrome():
    """A snippet that is mostly site chrome is suppressed (returns empty)."""
    chrome = "Skip to main content Subscribe Newsletter Log in Table of Contents"
    assert _clean_snippet(chrome) == ""


def test_clean_snippet_strips_video_metadata():
    """YouTube-style metadata lines are stripped and, if nothing's left, hidden."""
    meta = "Channel: The Fisherman Length: 51:45 Views: 2.9K Keywords: striper, bass"
    assert _clean_snippet(meta) == ""


def test_clean_snippet_preserves_useful_fishing_text():
    """Genuine fishing prose survives cleaning intact."""
    text = ("Stripers are migrating up the North Shore and hitting bucktails hard "
            "this week. Bloodworms and paddle tails both producing on the outgoing tide.")
    out = _clean_snippet(text)
    assert "Stripers are migrating" in out
    assert "bucktails" in out


def test_clean_snippet_removes_chrome_from_mixed_content():
    """Leading chrome is removed but the real content is kept."""
    text = ("Subscribe Newsletter Stripers crushing it at Plum Island mouth on "
            "the dropping tide, bucktails and soft plastics both working well today.")
    out = _clean_snippet(text)
    assert "Subscribe" not in out
    assert "Newsletter" not in out
    assert "Stripers crushing it at Plum Island" in out


def test_clean_snippet_rejects_script_fragments():
    """Markup/script fragments cause the snippet to be hidden."""
    text = "<div class='nav'>!function(){var x=1;}</div> something something"
    assert _clean_snippet(text) == ""


def test_clean_snippet_empty_input():
    assert _clean_snippet("") == ""
    assert _clean_snippet(None) == ""


# ── Title usefulness (drives drop-if-both-bad) ────────────────────────────────

def test_title_is_useful_accepts_real_title():
    assert _title_is_useful("Plum Island Striper Report - May 2026") is True


def test_title_is_useful_rejects_chrome_title():
    assert _title_is_useful("Subscribe to our Newsletter") is False


def test_title_is_useful_rejects_short_or_empty():
    assert _title_is_useful("") is False
    assert _title_is_useful("Login") is False


# ── Relevance gate ────────────────────────────────────────────────────────────

def test_is_relevant_drops_leading_chrome():
    assert _is_relevant("Subscribe", "Skip to main content Subscribe now") is False


def test_is_relevant_keeps_fishing_report():
    assert _is_relevant("Striper Report", "Bass and bait active on the tide") is True


# ── Empty-state language (must not sound broken) ──────────────────────────────

def test_web_report_empty_state_is_intentional():
    html = build_web_report_feed([])
    assert "throttled" not in html.lower()
    assert "error" not in html.lower()
    assert "matched the current source filters" in html


def test_reddit_empty_state_is_intentional():
    html = build_reddit_feed_html([])
    assert "throttled" not in html.lower()
    assert "no qualifying reddit signals" in html.lower()
