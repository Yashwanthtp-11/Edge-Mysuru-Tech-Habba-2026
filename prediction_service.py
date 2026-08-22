import os
import sys
import joblib
import pandas as pd
import numpy as np
import shap
from typing import Dict, Any, List, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.feature_engineering import add_time_features, add_lag_and_rolling_features

# Paths to saved joblib models
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLASSIFIER_PATH = os.path.join(BASE_DIR, "models", "rain_classifier.joblib")
REGRESSOR_PATH = os.path.join(BASE_DIR, "models", "rain_regressor.joblib")
FEATURE_COLS_PATH = os.path.join(BASE_DIR, "models", "feature_columns.joblib")


class PredictionService:
    def __init__(self):
        self.classifier = None
        self.regressor = None
        self.feature_columns = None
        self.shap_explainer = None
        self._load_models()

    def _load_models(self):
        """Loads trained ML models and feature columns list from joblib files."""
        if os.path.exists(CLASSIFIER_PATH) and os.path.exists(REGRESSOR_PATH) and os.path.exists(FEATURE_COLS_PATH):
            self.classifier = joblib.load(CLASSIFIER_PATH)
            self.regressor = joblib.load(REGRESSOR_PATH)
            self.feature_columns = joblib.load(FEATURE_COLS_PATH)
            
            # Initialize SHAP TreeExplainer for XGBoost classifier
            try:
                self.shap_explainer = shap.TreeExplainer(self.classifier)
            except Exception as e:
                print(f"Warning: Could not initialize SHAP explainer: {e}")
        else:
            print("Warning: ML models not found. Please train models using ml/evaluate.py first.")

    def is_ready(self) -> bool:
        return self.classifier is not None and self.regressor is not None and self.feature_columns is not None

    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """
        Applies time and lag/rolling feature engineering to raw Open-Meteo hourly dataframe
        and returns processed dataframe along with current hour row index.
        """
        df = add_time_features(df)
        df = add_lag_and_rolling_features(df)

        now = pd.Timestamp.now()
        if df["timestamp"].dt.tz is not None:
            df["timestamp"] = df["timestamp"].dt.tz_localize(None)

        current_idx = (df["timestamp"] - now).abs().idxmin()
        return df, current_idx

    def predict_current_and_hourly(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generates ML predictions for the current hour and next 24 forecast hours.
        """
        if not self.is_ready():
            self._load_models()
            if not self.is_ready():
                raise RuntimeError("ML Models are not trained or missing from models/ directory.")

        processed_df, current_idx = self.prepare_features(df)
        
        # Ensure all feature columns exist, fill missing with 0
        for col in self.feature_columns:
            if col not in processed_df.columns:
                processed_df[col] = 0.0

        X_all = processed_df[self.feature_columns].ffill().bfill().fillna(0.0)

        # Current Prediction
        X_current = X_all.iloc[[current_idx]]
        
        # Classifier probability %
        probs = self.classifier.predict_proba(X_current)[0]
        rain_prob = float(probs[1] * 100)
        rain_pred = bool(rain_prob >= 50.0)

        # Regressor precipitation amount (mm)
        log_pred = self.regressor.predict(X_current)[0]
        expected_mm = float(np.expm1(log_pred))
        expected_mm = max(0.0, round(expected_mm, 2))

        # Risk level determination
        if rain_prob > 75.0 or expected_mm > 10.0:
            risk_level = "HIGH"
        elif rain_prob > 40.0 or expected_mm > 2.5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Raw Open-Meteo forecast probability for comparison
        open_meteo_prob = float(processed_df.iloc[current_idx].get("precipitation_probability", 0.0))

        current_prediction = {
            "rain_probability": round(rain_prob, 1),
            "rain_prediction": rain_pred,
            "expected_rainfall_mm": expected_mm,
            "risk_level": risk_level,
            "open_meteo_probability": round(open_meteo_prob, 1)
        }

        # Next 24 hours forecast loop for interactive charts
        hourly_forecast = []
        future_indices = range(current_idx, min(current_idx + 24, len(processed_df)))

        for idx in future_indices:
            row_X = X_all.iloc[[idx]]
            row_prob = float(self.classifier.predict_proba(row_X)[0][1] * 100)
            row_log_precip = float(self.regressor.predict(row_X)[0])
            row_precip_mm = max(0.0, round(float(np.expm1(row_log_precip)), 2))
            
            row_time = str(processed_df.iloc[idx]["timestamp"])
            row_temp = float(processed_df.iloc[idx].get("temperature_2m", 0.0))
            row_hum = float(processed_df.iloc[idx].get("relative_humidity_2m", 0.0))

            hourly_forecast.append({
                "timestamp": row_time,
                "temperature": round(row_temp, 1),
                "humidity": round(row_hum, 1),
                "precipitation": row_precip_mm,
                "rain_probability": round(row_prob, 1)
            })

        return {
            "prediction": current_prediction,
            "hourly_forecast": hourly_forecast
        }

    def get_prediction_explanation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes SHAP feature importance for the current prediction vector.
        """
        if not self.is_ready():
            self._load_models()

        processed_df, current_idx = self.prepare_features(df)
        X_all = processed_df[self.feature_columns].ffill().bfill().fillna(0.0)
        X_current = X_all.iloc[[current_idx]]

        base_prob = float(self.classifier.predict_proba(X_current)[0][1] * 100)

        if self.shap_explainer is None:
            self.shap_explainer = shap.TreeExplainer(self.classifier)

        shap_values = self.shap_explainer(X_current)
        values = shap_values.values[0]

        # Map features to their SHAP impact
        feature_impacts = []
        for feat_name, val in zip(self.feature_columns, values):
            direction = "+++" if val > 0.05 else ("++" if val > 0.01 else ("+" if val > 0 else "-"))
            feature_impacts.append({
                "feature": feat_name,
                "impact_direction": direction,
                "importance_value": float(val)
            })

        # Sort by absolute SHAP importance value descending
        feature_impacts.sort(key=lambda x: abs(x["importance_value"]), reverse=True)
        top_factors = feature_impacts[:7]

        return {
            "top_factors": top_factors,
            "base_probability": round(base_prob, 1)
        }


# Singleton instance
prediction_service = PredictionService()
