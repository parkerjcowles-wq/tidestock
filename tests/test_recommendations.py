import pytest
from inventory.recommendations import (
    gross_margin,
    revenue_at_risk,
    urgency_score,
    confidence_label,
    fallback_buyer_brief,
    why_not_reorder,
)


def test_gross_margin_typical():
    assert abs(gross_margin(5.50, 9.99) - 0.4494) < 0.001


def test_gross_margin_zero_price():
    assert gross_margin(5.0, 0) == 0.0


def test_revenue_at_risk_below_rop():
    assert revenue_at_risk(on_hand=10, rop=20, retail_price=9.99) == pytest.approx(99.9)


def test_revenue_at_risk_above_rop():
    assert revenue_at_risk(on_hand=30, rop=20, retail_price=9.99) == 0.0


def test_urgency_score_increases_below_rop():
    score_above = urgency_score(
        on_hand=50, rop=20, dos=15, lead_time=5,
        fishing_score=60, striper_active=False, sku_key="terminal_tackle", margin=0.30,
    )
    score_below = urgency_score(
        on_hand=10, rop=20, dos=3, lead_time=5,
        fishing_score=60, striper_active=False, sku_key="terminal_tackle", margin=0.30,
    )
    assert score_below > score_above


def test_urgency_score_capped_at_100():
    score = urgency_score(
        on_hand=0, rop=100, dos=0, lead_time=7,
        fishing_score=90, striper_active=True, sku_key="soft_plastics", margin=0.50,
    )
    assert score <= 100


def test_confidence_label_high_when_all_signals_strong():
    label = confidence_label(
        on_hand=5, rop=20, dos=2, lead_time=5,
        fishing_score=80, striper_active=True, sku_key="soft_plastics",
    )
    assert label == "High"


def test_confidence_label_low_when_no_signals():
    label = confidence_label(
        on_hand=100, rop=20, dos=30, lead_time=5,
        fishing_score=40, striper_active=False, sku_key="accessories",
    )
    assert label == "Low"


def test_why_not_reorder_mentions_buffer():
    result = why_not_reorder(
        label="Soft Plastics", dos=20.0, lead_time=5, rop=30.0, on_hand=50.0,
    )
    assert "20" in result
    assert "no action" in result.lower()


def test_fallback_buyer_brief_with_flagged_items():
    ranked = [
        {"label": "Soft Plastics", "urgency": 55, "dos": 3.0, "lead_time": 5},
        {"label": "Hard Baits", "urgency": 10, "dos": 25.0, "lead_time": 5},
    ]
    brief = fallback_buyer_brief(ranked, species_active={"Striped Bass": "Peak"}, fishing_score=75)
    assert "Soft Plastics" in brief


def test_fallback_buyer_brief_all_healthy():
    ranked = [
        {"label": "Soft Plastics", "urgency": 5, "dos": 20.0, "lead_time": 5},
    ]
    brief = fallback_buyer_brief(ranked, species_active={}, fishing_score=50)
    assert "healthy" in brief.lower()
