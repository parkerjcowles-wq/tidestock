import pytest
from unittest.mock import MagicMock, patch
from signals.reddit_signals import extract_bait_mentions, classify_velocity

def test_extract_bait_mentions_finds_keyword():
    text = "Tried a paddle tail last night and crushed it"
    mentions = extract_bait_mentions(text, ["paddle tail", "ned rig"])
    assert "paddle tail" in mentions

def test_extract_bait_mentions_empty():
    assert extract_bait_mentions("no fishing terms here", ["ned rig"]) == []

def test_classify_velocity_trending():
    assert classify_velocity(upvotes=500, comments=80) == "trending"

def test_classify_velocity_elevated():
    assert classify_velocity(upvotes=150, comments=20) == "elevated"

def test_classify_velocity_baseline():
    assert classify_velocity(upvotes=20, comments=3) == "baseline"
