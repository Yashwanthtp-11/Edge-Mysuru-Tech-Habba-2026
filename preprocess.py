import os
import sys
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List

# Add parent directory to path to import ml.feature_engineering
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.feature_engineering import (
    add_time_features,
    add_lag_and_rolling_features,
    add_future_targets,
    get_feature_column_names,
)


def load_and_preprocess_data(
    input_path: str = "data/historical_weather.csv",
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Loads raw historical data, cleans duplicates, computes lag, rolling, time features and future targets.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Historical dataset not found at {input_path}. Please run scripts/download_data.py first.")

    df = pd.read_csv(input_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Remove duplicates
    if "latitude" in df.columns and "longitude" in df.columns:
        df = df.drop_duplicates(subset=["latitude", "longitude", "timestamp"])
        df = df.sort_values(by=["latitude", "longitude", "timestamp"]).reset_index(drop=True)
    else:
        df = df.drop_duplicates(subset=["timestamp"])
        df = df.sort_values(by="timestamp").reset_index(drop=True)

    # Ensure all required feature columns exist and fill missing values (100% NaN columns become 0.0)
    feature_cols = get_feature_column_names()
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = df[col].ffill().bfill().fillna(0.0)

    # Apply feature engineering
    df = add_time_features(df)
    df = add_lag_and_rolling_features(df)
    df = add_future_targets(df)

    # Drop NaN values introduced by shift operations on target columns and lag features
    target_cols = ["rain_next_1h", "rain_amount_next_1h"]
    df = df.dropna(subset=target_cols).reset_index(drop=True)
    df = df.ffill().bfill().fillna(0.0)

    return df, feature_cols


def chronological_train_val_test_split(
    df: pd.DataFrame, train_pct: float = 0.70, val_pct: float = 0.15
) -> Dict[str, pd.DataFrame]:
    """
    Splits time-series data CHRONOLOGICALLY into train (70%), validation (15%), and test (15%).
    DOES NOT randomly shuffle time-series data to avoid future data leakage.
    """
    # Ensure chronological order
    df = df.sort_values("timestamp").reset_index(drop=True)
    n = len(df)

    train_end = int(n * train_pct)
    val_end = int(n * (train_pct + val_pct))

    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()

    print(f"Chronological Dataset Split:")
    print(f"  Total samples: {n}")
    print(f"  Train samples: {len(train_df)} ({len(train_df)/n*100:.1f}%) | {train_df['timestamp'].min()} to {train_df['timestamp'].max()}")
    print(f"  Val samples:   {len(val_df)} ({len(val_df)/n*100:.1f}%) | {val_df['timestamp'].min()} to {val_df['timestamp'].max()}")
    print(f"  Test samples:  {len(test_df)} ({len(test_df)/n*100:.1f}%) | {test_df['timestamp'].min()} to {test_df['timestamp'].max()}")

    return {
        "train": train_df,
        "val": val_df,
        "test": test_df,
    }


if __name__ == "__main__":
    data_path = "data/historical_weather.csv"
    if os.path.exists(data_path):
        df, features = load_and_preprocess_data(data_path)
        splits = chronological_train_val_test_split(df)
        print("\nFeature Columns Count:", len(features))
        print("Positive Rain Class Balance in Train:", splits["train"]["rain_next_1h"].mean() * 100, "%")
    else:
        print(f"Run scripts/download_data.py first to generate {data_path}")
