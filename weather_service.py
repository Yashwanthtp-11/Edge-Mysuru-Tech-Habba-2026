import os
import requests
import pandas as pd
from typing import Dict, Any, Tuple
from datetime import datetime

FORECAST_API_URL = "https://api.open-meteo.com/v1/forecast"

HOURLY_FORECAST_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "showers",
    "snowfall",
    "pressure_msl",
    "surface_pressure",
    "cloud_cover",
    "cloud_cover_low",
    "cloud_cover_mid",
    "cloud_cover_high",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "visibility",
    "soil_temperature_0_to_7cm",
    "soil_moisture_0_to_7cm",
    "precipitation_probability",
]


def fetch_live_weather_and_history(lat: float, lon: float) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Fetches real-time weather, recent history (past 2 days), and forecast from Open-Meteo Forecast API.
    Returns:
      - df: Hourly dataframe containing past history + forecast hours for feature engineering.
      - current_weather: Dictionary of current observed weather metrics.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(HOURLY_FORECAST_VARIABLES),
        "past_days": 2,
        "forecast_days": 2,
        "timezone": "auto",
    }

    try:
        response = requests.get(FORECAST_API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Open-Meteo API connection failed: {e}")

    if "hourly" not in data:
        raise ValueError("Open-Meteo response missing 'hourly' data.")

    hourly_dict = data["hourly"]
    df = pd.DataFrame(hourly_dict)

    if "time" in df.columns:
        df.rename(columns={"time": "timestamp"}, inplace=True)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["latitude"] = lat
    df["longitude"] = lon

    # Forward fill missing values if any
    df = df.ffill().bfill()

    # Find row closest to current timestamp
    now = pd.Timestamp.now()
    # If timezone offset in data, remove tz or compare tz-naive
    if df["timestamp"].dt.tz is not None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(None)

    idx_current = (df["timestamp"] - now).abs().idxmin()
    current_row = df.iloc[idx_current]

    current_weather = {
        "temperature": float(current_row.get("temperature_2m", 0.0)),
        "humidity": float(current_row.get("relative_humidity_2m", 0.0)),
        "pressure": float(current_row.get("pressure_msl", current_row.get("surface_pressure", 1013.25))),
        "wind_speed": float(current_row.get("wind_speed_10m", 0.0)),
        "cloud_cover": float(current_row.get("cloud_cover", 0.0)),
        "timestamp": str(current_row.get("timestamp")),
        "precipitation_probability": float(current_row.get("precipitation_probability", 0.0))
    }

    return df, current_weather
