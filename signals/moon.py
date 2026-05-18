import datetime
import ephem

_PEAK_PHASES = {"new", "full"}

_PRESSURE_BONUS = {"rising": 20, "stable": 0, "falling": -20}

def get_moon_phase(date: datetime.date) -> str:
    m = ephem.Moon(date.isoformat())
    ill = m.moon_phase  # 0.0–1.0 illumination
    # Determine waxing vs waning from next full moon distance
    next_full = ephem.next_full_moon(date.isoformat()).datetime().date()
    days_to_full = (next_full - date).days
    waxing = days_to_full <= 14

    if ill < 0.02:
        return "new"
    if ill > 0.98:
        return "full"
    if waxing:
        return "waxing_crescent" if ill < 0.5 else "waxing_gibbous"
    else:
        return "waning_crescent" if ill < 0.5 else "waning_gibbous"

def get_fishing_score(moon_phase: str, pressure_trend: str) -> int:
    base = 90 if moon_phase in _PEAK_PHASES else 70 if "gibbous" in moon_phase else 50
    bonus = _PRESSURE_BONUS.get(pressure_trend, 0)
    return max(0, min(100, base + bonus))

def get_week_moon_data(start: datetime.date = None) -> list:
    if start is None:
        start = datetime.date.today()
    result = []
    for i in range(7):
        d = start + datetime.timedelta(days=i)
        phase = get_moon_phase(d)
        result.append({
            "date": d,
            "phase": phase,
            "score": get_fishing_score(phase, "stable"),
        })
    return result
