"""
src/forecast.py
Generate a single forecast for a given date, meal period, and menu item.
Uses the saved best model + residual std for the uncertainty range.

Uncertainty range note:
  The range is a HEURISTIC derived from model residuals on the test set.
  It is NOT a calibrated probability interval (e.g. not a 95% CI).
  It is clearly labelled as such in the UI.
"""

import numpy as np
import pandas as pd
from datetime import datetime

from src.models import load_best_model, load_model_results
from src.features import FEATURE_COLUMNS, ALL_MENU_ITEMS, _menu_col


def generate_forecast(
    date: str,
    meal_period: str,
    menu_item: str,
    is_special_event: int,
    attendance_estimate: int,
) -> dict:
    """
    Generate a point forecast with a heuristic uncertainty range.

    Parameters
    ----------
    date : str             YYYY-MM-DD
    meal_period : str      "Breakfast" | "Lunch" | "Dinner"
    menu_item : str        Name of the dish
    is_special_event : int 0 or 1
    attendance_estimate : int  Expected student count

    Returns
    -------
    dict with keys:
        forecast (int), lower (int), upper (int),
        model_name (str), risk_flags (list[str])
    """
    model = load_best_model()
    results = load_model_results()
    residual_std = results.get("residual_std", 20.0) if results else 20.0
    model_name = results.get("best_model", "Unknown") if results else "Unknown"

    # ── Build the single-row feature vector ──────────────────────────────────
    dt = datetime.strptime(date, "%Y-%m-%d")
    dow = dt.weekday()

    row = {
        "dow_sin": np.sin(2 * np.pi * dow / 7),
        "dow_cos": np.cos(2 * np.pi * dow / 7),
        "is_special_event": is_special_event,
        "attendance_estimate": attendance_estimate,
        # pre_orders is unknown at forecast time (the user hasn't placed orders
        # yet), so we default to 0. This matches what the model was trained on
        # for future-date rows in the synthetic dataset.
        "pre_orders": 0,
        "is_breakfast": int(meal_period == "Breakfast"),
        "is_lunch": int(meal_period == "Lunch"),
        "is_dinner": int(meal_period == "Dinner"),
    }

    # ── Menu item one-hot encoding (must mirror build_features) ───────────────
    for item in ALL_MENU_ITEMS:
        row[_menu_col(item)] = int(menu_item == item)

    X = np.array([[row[col] for col in FEATURE_COLUMNS]])
    point = float(model.predict(X)[0])
    point = max(0.0, point)

    # ── Heuristic uncertainty range (±1 residual std) ────────────────────────
    lower = max(0, int(round(point - residual_std)))
    upper = max(0, int(round(point + residual_std)))
    forecast = int(round(point))

    # ── Risk flags ────────────────────────────────────────────────────────────
    # These are rule-based indicators — NOT calibrated probabilities.
    risk_flags = []
    if is_special_event:
        risk_flags.append(
            "Special event detected — actual demand may be higher than the forecast."
        )
    if dow in (4, 5, 6):  # Friday, Saturday, Sunday
        risk_flags.append(
            "Weekend or end-of-week — attendance is typically lower."
        )
    if attendance_estimate > 600:
        risk_flags.append(
            "High attendance expected — consider preparing toward the upper range."
        )
    if attendance_estimate < 100:
        risk_flags.append(
            "Low attendance expected — preparing the lower range may reduce waste."
        )

    return {
        "forecast": forecast,
        "lower": lower,
        "upper": upper,
        "model_name": model_name,
        "risk_flags": risk_flags,
    }
