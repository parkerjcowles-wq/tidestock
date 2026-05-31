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


# ── New tests: additive perishable/seasonal params ────────────────────────────

def test_urgency_score_perishable_adds_8():
    base = urgency_score(
        on_hand=50, rop=20, dos=15, lead_time=5,
        fishing_score=40, striper_active=False, sku_key="accessories", margin=0.30,
        is_perishable=False,
    )
    perishable = urgency_score(
        on_hand=50, rop=20, dos=15, lead_time=5,
        fishing_score=40, striper_active=False, sku_key="accessories", margin=0.30,
        is_perishable=True,
    )
    assert perishable - base == 8


def test_urgency_score_overstock_perishable_adds_10():
    # dos=5 > shelf_life_days*0.85=3.4 → overstock spoilage risk (+10 on top of is_perishable +8)
    score = urgency_score(
        on_hand=50, rop=20, dos=5, lead_time=5,
        fishing_score=40, striper_active=False, sku_key="accessories", margin=0.30,
        is_perishable=True, shelf_life_days=4,
    )
    base = urgency_score(
        on_hand=50, rop=20, dos=5, lead_time=5,
        fishing_score=40, striper_active=False, sku_key="accessories", margin=0.30,
        is_perishable=False,
    )
    assert score - base == 18  # +8 perishable + +10 overstock


def test_urgency_score_is_seasonal_override():
    # sku_key="accessories" is not seasonal by default; passing is_seasonal=True should activate seasonal bonus
    with_seasonal = urgency_score(
        on_hand=50, rop=20, dos=15, lead_time=5,
        fishing_score=75, striper_active=False, sku_key="accessories", margin=0.30,
        is_seasonal=True,
    )
    without_seasonal = urgency_score(
        on_hand=50, rop=20, dos=15, lead_time=5,
        fishing_score=75, striper_active=False, sku_key="accessories", margin=0.30,
        is_seasonal=False,
    )
    assert with_seasonal > without_seasonal


def test_confidence_label_is_seasonal_override():
    # "accessories" is not seasonal; override to True with high fishing score should increase confidence
    from inventory.recommendations import confidence_label
    label_with = confidence_label(
        on_hand=5, rop=20, dos=2, lead_time=5,
        fishing_score=80, striper_active=True, sku_key="accessories",
        is_seasonal=True,
    )
    assert label_with == "High"


def test_reason_card_uses_species_tags_override():
    from inventory.recommendations import reason_card
    result = reason_card(
        sku_key="accessories", on_hand=5, rop=20, dos=2, lead_time=5,
        fishing_score=80, striper_active=True, margin=0.30,
        species_active={"Striped Bass": "Peak"},
        species_tags=["Striped Bass"],
    )
    assert "Striped Bass" in result["demand"]
