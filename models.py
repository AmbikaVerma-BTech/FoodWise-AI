"""
src/models.py
Train, evaluate, save, and load forecasting models.

Design decisions:
- Chronological train/test split (no shuffling) to prevent data leakage.
- All scores are from actual evaluation — never invented.
- Models saved with joblib for reproducible reload.
"""

from __future__ import annotations

import os
import json
import warnings
import numpy as np
import pandas as pd
import joblib

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.features import build_features, FEATURE_COLUMNS, TARGET_COLUMN

warnings.filterwarnings("ignore")

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
RESULTS_PATH = os.path.join(MODELS_DIR, "model_results.json")


def _wape(y_true, y_pred) -> float:
    """Weighted Absolute Percentage Error (lower is better)."""
    total_actual = np.sum(np.abs(y_true))
    if total_actual == 0:
        return float("nan")
    return float(np.sum(np.abs(y_true - y_pred)) / total_actual * 100)


def _rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def _naive_baseline(y_train: np.ndarray, y_test: np.ndarray) -> np.ndarray:
    """
    Naive baseline: predict the mean of the training target for every test row.
    Simplest possible forecast — every model must beat this.
    """
    return np.full_like(y_test, fill_value=y_train.mean(), dtype=float)


def train_and_evaluate_all(df: pd.DataFrame) -> dict:
    """
    Train all models on df, evaluate on chronological hold-out, save best model.

    Parameters
    ----------
    df : pd.DataFrame
        All meal records (real or synthetic).

    Returns
    -------
    dict with keys: metrics (list of dicts), best_model (str),
                    train_size (int), test_size (int),
                    feature_importance (list or None).
    """
    os.makedirs(MODELS_DIR, exist_ok=True)

    # ── Chronological split (no shuffle) ─────────────────────────────────────
    df_sorted = df.sort_values("date").reset_index(drop=True)
    split_idx = int(len(df_sorted) * 0.80)
    df_train = df_sorted.iloc[:split_idx]
    df_test  = df_sorted.iloc[split_idx:]

    X_train = build_features(df_train).values
    X_test  = build_features(df_test).values
    y_train = df_train[TARGET_COLUMN].values.astype(float)
    y_test  = df_test[TARGET_COLUMN].values.astype(float)

    # ── Models to compare ─────────────────────────────────────────────────────
    candidates = {
        "Naive Baseline": None,
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    }

    metrics = []
    best_mae = float("inf")
    best_name = None
    best_model = None

    for name, model in candidates.items():
        if model is None:
            y_pred = _naive_baseline(y_train, y_test)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

        mae  = float(mean_absolute_error(y_test, y_pred))
        rmse = _rmse(y_test, y_pred)
        wape = _wape(y_test, y_pred)

        metrics.append(
            {"model": name, "MAE": round(mae, 2), "RMSE": round(rmse, 2),
             "WAPE": round(wape, 2)}
        )

        if mae < best_mae:
            best_mae   = mae
            best_name  = name
            best_model = model

    # ── Save best model ───────────────────────────────────────────────────────
    # If the Naive Baseline won (best_model is None), we still need a callable
    # saved to disk so load_best_model() works. We wrap the training-mean in a
    # tiny sklearn-compatible object rather than leaving no file at all.
    if best_model is None:
        from sklearn.dummy import DummyRegressor
        best_model = DummyRegressor(strategy="mean")
        best_model.fit(X_train, y_train)

    joblib.dump(best_model, os.path.join(MODELS_DIR, "best_model.joblib"))

    # ── Feature importance (tree models only) ─────────────────────────────────
    feature_importance = None
    if hasattr(best_model, "feature_importances_"):
        feature_importance = list(
            zip(FEATURE_COLUMNS, best_model.feature_importances_.tolist())
        )

    # ── Residuals for uncertainty range ──────────────────────────────────────
    y_pred_best = best_model.predict(X_test)

    residuals = y_test - y_pred_best
    residual_std = float(np.std(residuals))

    results = {
        "metrics": metrics,
        "best_model": best_name,
        "train_size": len(df_train),
        "test_size":  len(df_test),
        "feature_importance": feature_importance,
        "residual_std": residual_std,
        "feature_columns": FEATURE_COLUMNS,
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    return results


def load_model_results() -> dict | None:
    """Load saved model results from disk. Returns None if not found."""
    if not os.path.exists(RESULTS_PATH):
        return None
    with open(RESULTS_PATH) as f:
        return json.load(f)


def load_best_model():
    """Load the saved best model. Raises FileNotFoundError if not trained yet."""
    model_path = os.path.join(MODELS_DIR, "best_model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            "No trained model found. Train models on the Model Performance page first."
        )
    return joblib.load(model_path)
