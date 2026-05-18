import pytest
import responses as resp_mock
from signals.noaa import fetch_tide_predictions, fetch_water_temp, classify_tide_quality

MOCK_TIDE_RESPONSE = {
    "predictions": [
        {"t": "2026-05-18 00:00", "v": "2.1"},
        {"t": "2026-05-18 06:00", "v": "8.9"},
        {"t": "2026-05-18 12:00", "v": "1.8"},
        {"t": "2026-05-18 18:00", "v": "9.2"},
    ]
}

MOCK_TEMP_RESPONSE = {
    "data": [{"t": "2026-05-18 12:00", "v": "56.3"}]
}

@resp_mock.activate
def test_fetch_tide_predictions_returns_dataframe():
    import pandas as pd
    resp_mock.add(resp_mock.GET, "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
                  json=MOCK_TIDE_RESPONSE, status=200)
    df = fetch_tide_predictions("8440625", days=1)
    assert isinstance(df, pd.DataFrame)
    assert "time" in df.columns and "height" in df.columns
    assert len(df) == 4

@resp_mock.activate
def test_fetch_water_temp_returns_float():
    resp_mock.add(resp_mock.GET, "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
                  json=MOCK_TEMP_RESPONSE, status=200)
    temp = fetch_water_temp("8440625")
    assert isinstance(temp, float)
    assert abs(temp - 56.3) < 0.1

def test_classify_tide_quality_prime():
    assert classify_tide_quality(max_range=8.5, num_peaks=2) == "prime"

def test_classify_tide_quality_moderate():
    assert classify_tide_quality(max_range=4.0, num_peaks=2) == "moderate"

def test_classify_tide_quality_poor():
    assert classify_tide_quality(max_range=1.5, num_peaks=1) == "poor"

@resp_mock.activate
def test_fetch_tide_predictions_empty_response():
    import pandas as pd
    resp_mock.add(resp_mock.GET, "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
                  json={"predictions": []}, status=200)
    df = fetch_tide_predictions("8440625", days=1)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["time", "height"]
    assert len(df) == 0

@resp_mock.activate
def test_fetch_tide_predictions_noaa_error_body():
    resp_mock.add(resp_mock.GET, "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
                  json={"error": {"message": "No data was found"}}, status=200)
    with pytest.raises(ValueError, match="No data was found"):
        fetch_tide_predictions("9999999", days=1)

def test_classify_tide_quality_moderate_ignores_peaks():
    # moderate range qualifies regardless of peak count — only prime gates on peaks
    assert classify_tide_quality(max_range=4.0, num_peaks=0) == "moderate"
