from inventory.forecast import compute_demand_index, compute_scenario_demand, DEFAULT_WEIGHTS

def test_baseline_demand_unchanged_at_equal_weights():
    index = compute_demand_index(
        base_demand=100,
        moon_phase="first_quarter",
        tide_quality="moderate",
        social_velocity="baseline",
        pressure_trend="stable",
        tournament_proximity="none",
        season_level="shoulder",
        weights=DEFAULT_WEIGHTS,
    )
    assert 90 <= index <= 130  # near baseline with neutral signals

def test_peak_conditions_increase_demand():
    high = compute_demand_index(
        base_demand=100, moon_phase="full", tide_quality="prime",
        social_velocity="trending", pressure_trend="rising",
        tournament_proximity="within_3_days", season_level="peak",
        weights=DEFAULT_WEIGHTS,
    )
    low = compute_demand_index(
        base_demand=100, moon_phase="waning_crescent", tide_quality="poor",
        social_velocity="baseline", pressure_trend="falling",
        tournament_proximity="none", season_level="off",
        weights=DEFAULT_WEIGHTS,
    )
    assert high > low

def test_zero_weight_signal_ignored():
    weights = {**DEFAULT_WEIGHTS, "tournament": 0.0}
    with_tournament = compute_demand_index(
        base_demand=100, moon_phase="full", tide_quality="prime",
        social_velocity="baseline", pressure_trend="stable",
        tournament_proximity="within_3_days", season_level="peak",
        weights=DEFAULT_WEIGHTS,
    )
    without_tournament = compute_demand_index(
        base_demand=100, moon_phase="full", tide_quality="prime",
        social_velocity="baseline", pressure_trend="stable",
        tournament_proximity="within_3_days", season_level="peak",
        weights=weights,
    )
    assert without_tournament < with_tournament

def test_scenario_tournament_spikes_finesse():
    result = compute_scenario_demand({"terminal_tackle": 60}, "tournament_weekend")
    assert result["terminal_tackle"] > 60

def test_scenario_viral_bait_spikes_soft_plastics():
    result = compute_scenario_demand({"soft_plastics": 35}, "viral_bait_moment")
    assert result["soft_plastics"] > 35 * 2
