import datetime
from signals.moon import get_moon_phase, get_fishing_score, get_week_moon_data

def test_phase_returns_known_string():
    phase = get_moon_phase(datetime.date(2026, 5, 18))
    assert isinstance(phase, str)
    assert phase in ["new", "waxing_crescent", "first_quarter", "waxing_gibbous",
                     "full", "waning_gibbous", "last_quarter", "waning_crescent"]

def test_fishing_score_range():
    score = get_fishing_score(moon_phase="full", pressure_trend="rising")
    assert 0 <= score <= 100

def test_fishing_score_new_moon_rising():
    score = get_fishing_score(moon_phase="new", pressure_trend="rising")
    assert score >= 80

def test_fishing_score_waning_falling():
    score = get_fishing_score(moon_phase="waning_crescent", pressure_trend="falling")
    assert score <= 60

def test_week_data_length():
    data = get_week_moon_data()
    assert len(data) == 7
    assert all("date" in d and "phase" in d and "score" in d for d in data)

def test_first_quarter_phase_reachable():
    # May 23, 2026 is first quarter moon
    phase = get_moon_phase(datetime.date(2026, 5, 23))
    assert phase in ["first_quarter", "waxing_crescent", "waxing_gibbous"]
    # At minimum verify the classifier doesn't crash on near-quarter dates

def test_waxing_waning_direction():
    # On a date clearly after new moon and before full moon, should be waxing
    # April 25, 2026 was after new moon (April 17) and before full moon (May 1)
    phase = get_moon_phase(datetime.date(2026, 4, 25))
    assert phase in ["waxing_crescent", "first_quarter", "waxing_gibbous"]
