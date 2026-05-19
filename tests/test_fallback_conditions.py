from signals.fallback import fallback_conditions


def test_fallback_tide_df_has_correct_columns():
    cond = fallback_conditions()
    assert list(cond["tide_df"].columns) == ["time", "height"]
    assert len(cond["tide_df"]) == 0


def test_fallback_water_temp_is_default():
    cond = fallback_conditions()
    assert cond["water_temp"] == 55.0


def test_fallback_pressure_trend_is_stable():
    cond = fallback_conditions()
    assert cond["weather"]["pressure_trend"] == "stable"


def test_fallback_fishing_score_is_valid():
    cond = fallback_conditions()
    assert 0 <= cond["fishing_score"] <= 100


def test_fallback_pressure_series_has_correct_columns():
    cond = fallback_conditions()
    assert list(cond["weather"]["pressure_series"].columns) == ["time", "pressure"]
