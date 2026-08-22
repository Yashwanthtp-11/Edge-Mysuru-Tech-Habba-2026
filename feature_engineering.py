import numpy as np
import pandas as pd
from typing import List, Tuple

# Base features required for feature engineering
BASE_WEATHER_COLUMNS = [
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
]


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adds cyclic time encodings (sin/cos for hour and month) and integer time features."""
    df = df.copy()
    if "timestamp" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    if "timestamp" in df.columns:
        df["hour"] = df["timestamp"].dt.hour
        df["day"] = df["timestamp"].dt.day
        df["month"] = df["timestamp"].dt.month
        df["day_of_year"] = df["timestamp"].dt.dayofyear

    # Sine/Cosine cyclical encodings
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24.0)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24.0)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)

    return df


def add_lag_and_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates lag and rolling window features for precipitation, humidity, temperature, and pressure.
    Supports both single-location and multi-location (grouped by location) dataframes.
    """
    df = df.copy()

    # Determine group columns if latitude/longitude exist
    has_groups = "latitude" in df.columns and "longitude" in df.columns

    def process_group(group_df: pd.DataFrame) -> pd.DataFrame:
        group_df = group_df.sort_values("timestamp")

        # Total rainfall is sum of rain + showers (precipitation)
        precip = group_df["precipitation"] if "precipitation" in group_df.columns else group_df["rain"]

        # Lag features
        group_df["rainfall_previous_hour"] = precip.shift(1)
        group_df["rainfall_previous_3_hours"] = precip.shift(3)
        group_df["rainfall_previous_6_hours"] = precip.shift(6)
        group_df["rainfall_previous_12_hours"] = precip.shift(12)
        group_df["rainfall_previous_24_hours"] = precip.shift(24)

        # Rolling features (using closed='left' or shift to avoid current row leakage in rolling)
        precip_shifted = precip.shift(1)
        group_df["rainfall_rolling_3h"] = precip_shifted.rolling(window=3, min_periods=1).mean()
        group_df["rainfall_rolling_6h"] = precip_shifted.rolling(window=6, min_periods=1).mean()
        group_df["rainfall_rolling_24h"] = precip_shifted.rolling(window=24, min_periods=1).mean()

        humidity_shifted = group_df["relative_humidity_2m"].shift(1)
        group_df["humidity_rolling_6h"] = humidity_shifted.rolling(window=6, min_periods=1).mean()

        temp_shifted = group_df["temperature_2m"].shift(1)
        group_df["temperature_rolling_6h"] = temp_shifted.rolling(window=6, min_periods=1).mean()

        pressure = group_df["pressure_msl"] if "pressure_msl" in group_df.columns else group_df["surface_pressure"]
        pressure_shifted = pressure.shift(1)
        group_df["pressure_rolling_6h"] = pressure_shifted.rolling(window=6, min_periods=1).mean()

        return group_df

    if has_groups:
        df = df.groupby(["latitude", "longitude"], group_keys=False).apply(process_group)
    else:
        df = process_group(df)

    return df


def add_future_targets(df: pd.DataFrame, threshold_mm: float = 0.1) -> pd.DataFrame:
    """
    Creates target variables for future 1-hour predictions:
    - rain_next_1h: binary classification target (1 if precipitation in next 1h > threshold_mm, else 0)
    - rain_amount_next_1h: regression target (precipitation in next 1h)
    """
    df = df.copy()

    has_groups = "latitude" in df.columns and "longitude" in df.columns

    def add_targets_to_group(group_df: pd.DataFrame) -> pd.DataFrame:
        group_df = group_df.sort_values("timestamp")
        precip = group_df["precipitation"] if "precipitation" in group_df.columns else group_df["rain"]
        
        # Future 1-hour precipitation target (shift -1)
        group_df["rain_amount_next_1h"] = precip.shift(-1)
        group_df["rain_next_1h"] = (group_df["rain_amount_next_1h"] > threshold_mm).astype(int)
        return group_df

    if has_groups:
        df = df.groupby(["latitude", "longitude"], group_keys=False).apply(add_targets_to_group)
    else:
        df = add_targets_to_group(df)

    return df


def get_feature_column_names() -> List[str]:
    """Returns the exact list of feature names used by the ML models."""
    return [
        "hour",
        "day",
        "month",
        "day_of_year",
        "hour_sin",
        "hour_cos",
        "month_sin",
        "month_cos",
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
        "rainfall_previous_hour",
        "rainfall_previous_3_hours",
        "rainfall_previous_6_hours",
        "rainfall_previous_12_hours",
        "rainfall_previous_24_hours",
        "rainfall_rolling_3h",
        "rainfall_rolling_6h",
        "rainfall_rolling_24h",
        "humidity_rolling_6h",
        "temperature_rolling_6h",
        "pressure_rolling_6h",
    ]
