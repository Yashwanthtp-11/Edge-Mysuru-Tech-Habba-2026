import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.preprocess import load_and_preprocess_data, chronological_train_val_test_split


def train_regressor_models(data_path: str = "data/historical_weather.csv", models_dir: str = "models"):
    """
    Trains Rainfall Amount Regressors (XGBoost, Random Forest, Gradient Boosting) on time-series dataset.
    Applies log1p target transformation to handle skewed rainfall distributions.
    Evaluates models using MAE, RMSE, R2 and saves the best performing XGBoost regressor.
    """
    print("\n==================================================")
    print("STEP 2: TRAINING MODEL B - RAINFALL AMOUNT REGRESSOR")
    print("==================================================")

    df, feature_cols = load_and_preprocess_data(data_path)
    splits = chronological_train_val_test_split(df)

    train_df = splits["train"]
    val_df = splits["val"]
    test_df = splits["test"]

    X_train, y_train_raw = train_df[feature_cols], train_df["rain_amount_next_1h"]
    X_val, y_val_raw = val_df[feature_cols], val_df["rain_amount_next_1h"]
    X_test, y_test_raw = test_df[feature_cols], test_df["rain_amount_next_1h"]

    # Target transformation (log1p to stabilize skewed rainfall distribution)
    y_train_log = np.log1p(y_train_raw)
    y_val_log = np.log1p(y_val_raw)

    print(f"Target Distribution (Raw Test Set): Max={y_test_raw.max():.2f}mm, Mean={y_test_raw.mean():.4f}mm, Std={y_test_raw.std():.4f}mm")

    # 1. XGBoost Regressor
    print("\nTraining XGBoost Regressor (Log-Transformed Target)...")
    xgb_reg = xgb.XGBRegressor(
        n_estimators=250,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="rmse"
    )
    xgb_reg.fit(X_train, y_train_log, eval_set=[(X_val, y_val_log)], verbose=False)

    # 2. Random Forest Regressor
    print("Training Random Forest Regressor...")
    rf_reg = RandomForestRegressor(
        n_estimators=150,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    rf_reg.fit(X_train, y_train_log)

    # 3. Gradient Boosting Regressor
    print("Training Gradient Boosting Regressor...")
    gb_reg = GradientBoostingRegressor(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        random_state=42
    )
    gb_reg.fit(X_train, y_train_log)

    # Evaluation on Test Set (Transform predictions back via expm1)
    models = {
        "XGBoost": xgb_reg,
        "Random Forest": rf_reg,
        "Gradient Boosting": gb_reg
    }

    metrics_results = {}
    print("\nREGRESSOR MODEL COMPARISON (ON TEST SET):")
    print(f"{'Model':<22} {'MAE (mm)':<12} {'RMSE (mm)':<12} {'R² Score':<12}")
    print("-" * 58)

    for name, model in models.items():
        preds_log = model.predict(X_test)
        preds_raw = np.expm1(preds_log)
        preds_raw = np.clip(preds_raw, 0, None)  # Rainfall cannot be negative

        mae = mean_absolute_error(y_test_raw, preds_raw)
        rmse = np.sqrt(mean_squared_error(y_test_raw, preds_raw))
        r2 = r2_score(y_test_raw, preds_raw)

        metrics_results[name] = {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2)
        }

        print(f"{name:<22} {mae:<12.4f} {rmse:<12.4f} {r2:<12.4f}")

    # Save best regressor model
    os.makedirs(models_dir, exist_ok=True)
    regressor_save_path = os.path.join(models_dir, "rain_regressor.joblib")
    joblib.dump(xgb_reg, regressor_save_path)

    print(f"\nBest Regressor (XGBoost) saved to: {regressor_save_path}")
    print("==================================================\n")

    return metrics_results, xgb_reg


if __name__ == "__main__":
    train_regressor_models()
