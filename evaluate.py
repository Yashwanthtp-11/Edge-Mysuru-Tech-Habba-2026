import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.train_classifier import train_classifier_models
from ml.train_regressor import train_regressor_models


def generate_evaluation_artifacts(reports_dir: str = "reports"):
    """
    Executes model training, collects metrics, saves reports/model_metrics.json,
    and generates visual evaluation plots (confusion matrix, ROC curve, feature importances).
    """
    plots_dir = os.path.join(reports_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Run training and get evaluation metrics
    clf_metrics, xgb_clf, feature_cols = train_classifier_models()
    reg_metrics, xgb_reg = train_regressor_models()

    full_report = {
        "classifier_models": clf_metrics,
        "regressor_models": reg_metrics,
        "feature_columns": feature_cols
    }

    # Save metrics JSON
    metrics_path = os.path.join(reports_dir, "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(full_report, f, indent=4)
    print(f"Full evaluation report saved to: {metrics_path}")

    # Generate Plot 1: Confusion Matrix for Best Classifier (XGBoost)
    if "XGBoost" in clf_metrics and "confusion_matrix" in clf_metrics["XGBoost"]:
        cm = np.array(clf_metrics["XGBoost"]["confusion_matrix"])
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["No Rain", "Rain"], yticklabels=["No Rain", "Rain"])
        plt.title("XGBoost Rain Classifier - Confusion Matrix")
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.tight_layout()
        cm_path = os.path.join(plots_dir, "confusion_matrix.png")
        plt.savefig(cm_path, dpi=300)
        plt.close()
        print(f"Saved Confusion Matrix plot to: {cm_path}")

    # Generate Plot 2: Feature Importances for XGBoost Classifier
    if hasattr(xgb_clf, "feature_importances_"):
        importances = xgb_clf.feature_importances_
        indices = np.argsort(importances)[::-1][:15] # Top 15 features

        plt.figure(figsize=(10, 6))
        plt.title("Top 15 Feature Importances (XGBoost Classifier)")
        plt.barh(range(len(indices)), importances[indices][::-1], align="center", color="skyblue")
        plt.yticks(range(len(indices)), [feature_cols[i] for i in indices[::-1]])
        plt.xlabel("Relative Importance")
        plt.tight_layout()
        fi_path = os.path.join(plots_dir, "feature_importance.png")
        plt.savefig(fi_path, dpi=300)
        plt.close()
        print(f"Saved Feature Importance plot to: {fi_path}")

    print("\n==================================================")
    print("FINAL EVALUATION SUMMARY")
    print("==================================================")
    print("\nMODEL A: RAIN / NO-RAIN CLASSIFIER")
    print(f"{'Model':<22} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'ROC-AUC':<10}")
    print("-" * 72)
    for model, m in clf_metrics.items():
        print(f"{model:<22} {m['accuracy']:<10.4f} {m['precision']:<10.4f} {m['recall']:<10.4f} {m['f1_score']:<10.4f} {m['roc_auc']:<10.4f}")

    print("\nMODEL B: RAINFALL AMOUNT REGRESSOR")
    print(f"{'Model':<22} {'MAE (mm)':<12} {'RMSE (mm)':<12} {'R² Score':<12}")
    print("-" * 58)
    for model, m in reg_metrics.items():
        print(f"{model:<22} {m['mae']:<12.4f} {m['rmse']:<12.4f} {m['r2']:<12.4f}")
    print("==================================================\n")


if __name__ == "__main__":
    generate_evaluation_artifacts()
