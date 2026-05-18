import responses as resp_mock
from signals.weather import fetch_weather, classify_pressure_trend

MOCK_WEATHER = {
    "hourly": {
        "time": ["2026-05-18T00:00", "2026-05-18T06:00", "2026-05-18T12:00"],
        "pressure_msl": [1015.0, 1013.0, 1010.0],
        "temperature_2m": [55.0, 57.0, 60.0],
        "wind_speed_10m": [8.0, 10.0, 12.0],
    }
}

@resp_mock.activate
def test_fetch_weather_returns_expected_keys():
    resp_mock.add(resp_mock.GET, "https://api.open-meteo.com/v1/forecast",
                  json=MOCK_WEATHER, status=200)
    result = fetch_weather(42.8126, -70.8773)
    assert "pressure_series" in result
    assert "current_temp_f" in result
    assert "pressure_trend" in result

def test_classify_falling():
    assert classify_pressure_trend([1015, 1013, 1010]) == "falling"

def test_classify_rising():
    assert classify_pressure_trend([1008, 1011, 1015]) == "rising"

def test_classify_stable():
    assert classify_pressure_trend([1013, 1013, 1014]) == "stable"
