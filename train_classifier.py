import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import xgboost as xgb

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.preprocess import load_and_preprocess_data, chronological_train_val_test_split


def train_classifier_models(data_path: str = "data/historical_weather.csv", models_dir: str = "models"):
    """
    Trains Rain/No-Rain Classifiers (XGBoost, Random Forest, Logistic Regression) on time-series dataset.
    Evaluates models, saves the best performing XGBoost classifier and feature columns.
    """
    print("\n==================================================")
    print("STEP 1: TRAINING MODEL A - RAIN / NO-RAIN CLASSIFIER")
    print("==================================================")

    df, feature_cols = load_and_preprocess_data(data_path)
    splits = chronological_train_val_test_split(df)

    train_df = splits["train"]
    val_df = splits["val"]
    test_df = splits["test"]

    X_train, y_train = train_df[feature_cols], train_df["rain_next_1h"]
    X_val, y_val = val_df[feature_cols], val_df["rain_next_1h"]
    X_test, y_test = test_df[feature_cols], test_df["rain_next_1h"]

    # Calculate class weight for imbalanced rainfall target
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos_weight = neg_count / max(pos_count, 1)

    print(f"Class Distribution in Training Set: Negative (No Rain)={neg_count}, Positive (Rain)={pos_count} (scale_pos_weight={scale_pos_weight:.2f})")

    # 1. XGBoost Classifier
    print("\nTraining XGBoost Classifier...")
    xgb_clf = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric="logloss"
    )
    xgb_clf.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

    # 2. Random Forest Classifier
    print("Training Random Forest Classifier...")
    rf_clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    rf_clf.fit(X_train, y_train)

    # 3. Logistic Regression (with Feature Scaling)
    print("Training Logistic Regression...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    lr_clf = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    lr_clf.fit(X_train_scaled, y_train)

    # Evaluation on Validation and Test Sets
    models = {
        "XGBoost": (xgb_clf, X_test, y_test),
        "Random Forest": (rf_clf, X_test, y_test),
        "Logistic Regression": (lr_clf, X_test_scaled, y_test)
    }

    metrics_results = {}
    print("\nCLASSIFIER MODEL COMPARISON (ON TEST SET):")
    print(f"{'Model':<22} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'ROC-AUC':<10}")
    print("-" * 72)

    for name, (model, X_eval, y_eval) in models.items():
        preds = model.predict(X_eval)
        probs = model.predict_proba(X_eval)[:, 1] if hasattr(model, "predict_proba") else preds

        acc = accuracy_score(y_eval, preds)
        prec = precision_score(y_eval, preds, zero_division=0)
        rec = recall_score(y_eval, preds, zero_division=0)
        f1 = f1_score(y_eval, preds, zero_division=0)
        try:
            auc = roc_auc_score(y_eval, probs)
        except Exception:
            auc = 0.0

        cm = confusion_matrix(y_eval, preds).tolist()

        metrics_results[name] = {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1),
            "roc_auc": float(auc),
            "confusion_matrix": cm
        }

        print(f"{name:<22} {acc:<10.4f} {prec:<10.4f} {rec:<10.4f} {f1:<10.4f} {auc:<10.4f}")

    # Save models & feature list
    os.makedirs(models_dir, exist_ok=True)
    classifier_save_path = os.path.join(models_dir, "rain_classifier.joblib")
    features_save_path = os.path.join(models_dir, "feature_columns.joblib")

    joblib.dump(xgb_clf, classifier_save_path)
    joblib.dump(feature_cols, features_save_path)

    print(f"\nBest Classifier (XGBoost) saved to: {classifier_save_path}")
    print(f"Feature columns saved to: {features_save_path}")
    print("==================================================\n")

    return metrics_results, xgb_clf, feature_cols


if __name__ == "__main__":
    train_classifier_models()
