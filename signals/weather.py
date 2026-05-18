import requests
import pandas as pd

_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_weather(lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pressure_msl,temperature_2m,wind_speed_10m",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "forecast_days": 3,
    }
    r = requests.get(_OPEN_METEO_URL, params=params, timeout=10)
    r.raise_for_status()
    hourly = r.json()["hourly"]
    df = pd.DataFrame({
        "time": pd.to_datetime(hourly["time"]),
        "pressure": hourly["pressure_msl"],
        "temp_f": hourly["temperature_2m"],
        "wind_mph": hourly["wind_speed_10m"],
    })
    pressures = df["pressure"].tolist()
    return {
        "pressure_series": df[["time", "pressure"]],
        "current_temp_f": df["temp_f"].iloc[0],
        "current_wind_mph": df["wind_mph"].iloc[0],
        "pressure_trend": classify_pressure_trend(pressures[:12]),  # 12-hour window
    }

def classify_pressure_trend(pressures: list) -> str:
    if len(pressures) < 2:
        return "stable"
    delta = pressures[-1] - pressures[0]
    if delta > 1.5:
        return "rising"
    if delta < -1.5:
        return "falling"
    return "stable"
