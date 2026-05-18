import requests
import pandas as pd
import datetime

_BASE = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

def fetch_tide_predictions(station_id, days=7):
    # type: (str, int) -> pd.DataFrame
    """
    Fetch tide predictions from NOAA for the given station.

    Args:
        station_id: NOAA station ID (e.g., '8440625' for Gloucester, MA)
        days: Number of days to fetch (default 7)

    Returns:
        DataFrame with 'time' and 'height' columns
    """
    today = datetime.date.today()
    end = today + datetime.timedelta(days=days)
    params = {
        "station": station_id,
        "product": "predictions",
        "datum": "MLLW",
        "time_zone": "lst_ldt",
        "interval": "h",
        "units": "english",
        "begin_date": today.strftime("%Y%m%d"),
        "end_date": end.strftime("%Y%m%d"),
        "application": "tidestock",
        "format": "json",
    }
    r = requests.get(_BASE, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get("predictions", [])
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["t"])
    df["height"] = df["v"].astype(float)
    return df[["time", "height"]]

def fetch_water_temp(station_id):
    # type: (str) -> float
    """
    Fetch water temperature from NOAA for the given station.

    Args:
        station_id: NOAA station ID (e.g., '8440625' for Gloucester, MA)

    Returns:
        Water temperature in Fahrenheit (float). Returns 55.0 if no data available.
    """
    params = {
        "station": station_id,
        "product": "water_temperature",
        "datum": "MLLW",
        "time_zone": "lst_ldt",
        "units": "english",
        "range": "24",
        "application": "tidestock",
        "format": "json",
    }
    r = requests.get(_BASE, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get("data", [])
    if not data:
        return 55.0  # fallback if station doesn't report temp
    return float(data[-1]["v"])

def classify_tide_quality(max_range, num_peaks):
    # type: (float, int) -> str
    """
    Classify tide quality based on range and number of peaks.

    Args:
        max_range: Maximum tide height range in feet
        num_peaks: Number of tidal peaks in the period

    Returns:
        One of: 'prime', 'moderate', 'poor'
    """
    if max_range >= 6.0 and num_peaks >= 2:
        return "prime"
    if max_range >= 3.0:
        return "moderate"
    return "poor"

def get_tide_quality(df):
    # type: (pd.DataFrame) -> str
    """
    Compute tide quality from a tide predictions DataFrame.

    Args:
        df: DataFrame with 'height' column (from fetch_tide_predictions)

    Returns:
        One of: 'prime', 'moderate', 'poor'
    """
    if df.empty:
        return "moderate"
    max_range = df["height"].max() - df["height"].min()
    heights = df["height"].values
    peaks = sum(
        1 for i in range(1, len(heights) - 1)
        if heights[i] > heights[i-1] and heights[i] > heights[i+1]
    )
    return classify_tide_quality(max_range, peaks)
