import pytest
from charts.scenario import build_scenario_comparison, _scenario_bar_colors


def _labels():
    return {"soft_plastics": "Soft Plastics", "hard_baits": "Hard Baits", "bait": "Live Bait"}


def test_scenario_bar_colors_elevated():
    """Category with >5% demand increase gets red."""
    baseline = {"soft_plastics": 100, "hard_baits": 100}
    scenario = {"soft_plastics": 200, "hard_baits": 100}
    colors = _scenario_bar_colors(baseline, scenario)
    assert colors[0] == "#f87171"   # soft_plastics up 100% → red
    assert colors[1] == "#4ade80"   # hard_baits unchanged → green


def test_scenario_bar_colors_flat():
    """Category at exactly baseline gets green."""
    baseline = {"bait": 50}
    scenario = {"bait": 50}
    colors = _scenario_bar_colors(baseline, scenario)
    assert colors[0] == "#4ade80"


def test_scenario_bar_colors_threshold():
    """Category at exactly 5% increase stays green (threshold is strictly >5%)."""
    baseline = {"bait": 100}
    scenario = {"bait": 105}
    colors = _scenario_bar_colors(baseline, scenario)
    assert colors[0] == "#4ade80"


def test_scenario_bar_colors_above_threshold():
    """Category at 6% increase gets red."""
    baseline = {"bait": 100}
    scenario = {"bait": 106}
    colors = _scenario_bar_colors(baseline, scenario)
    assert colors[0] == "#f87171"


def test_build_scenario_comparison_returns_figure():
    """build_scenario_comparison returns a plotly Figure with 4 traces (2 data + 2 legend dummies)."""
    import plotly.graph_objects as go
    baseline = {"soft_plastics": 100, "hard_baits": 80}
    scenario = {"soft_plastics": 300, "hard_baits": 80}
    fig = build_scenario_comparison(baseline, scenario, _labels(), subtitle="Viral Bait Moment")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 4


def test_build_scenario_comparison_baseline_gray():
    """Baseline bars are all the same gray color."""
    baseline = {"soft_plastics": 100, "hard_baits": 80}
    scenario = {"soft_plastics": 300, "hard_baits": 80}
    fig = build_scenario_comparison(baseline, scenario, _labels())
    baseline_trace = fig.data[0]
    assert baseline_trace.marker.color == "#2a2a2e"


def test_build_scenario_comparison_scenario_colors_are_list():
    """Scenario bars use a list of colors (not a single color)."""
    baseline = {"soft_plastics": 100, "hard_baits": 80}
    scenario = {"soft_plastics": 300, "hard_baits": 80}
    fig = build_scenario_comparison(baseline, scenario, _labels())
    scenario_trace = fig.data[1]
    assert isinstance(scenario_trace.marker.color, (list, tuple))


def test_scenario_bar_colors_zero_baseline():
    """Zero baseline is treated as unchanged (can't compute pct — avoid division by zero)."""
    colors = _scenario_bar_colors({"bait": 0}, {"bait": 999})
    assert colors[0] == "#4ade80"


def test_scenario_bar_colors_decrease_is_green():
    """Demand decrease is treated as unchanged — a drop is not a restock alert."""
    baseline = {"bait": 100}
    scenario = {"bait": 60}
    colors = _scenario_bar_colors(baseline, scenario)
    assert colors[0] == "#4ade80"
