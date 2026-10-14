"""
src/features.py
Build ML feature columns from raw meal records DataFrame.
All feature engineering lives here to keep models.py clean.
"""

import pandas as pd
import numpy as np


# All known menu items across all meal periods (used for one-hot encoding).
ALL_MENU_ITEMS = [
    # Breakfast
    "Idli & Sambar", "Poha", "Bread & Omelette", "Upma", "Paratha",
    # Lunch / Dinner shared
    "Rice & Curry", "Dal & Roti", "Fried Rice", "Noodles", "Pasta",
    # Dinner-specific
    "Soup", "Sandwich", "Salad Bowl",
]

# Ordered list of feature column names used by all models.
# Any change here must be reflected in saved models (retrain if changed).
FEATURE_COLUMNS = (
    [
        "dow_sin",
        "dow_cos",
        "is_special_event",
        "attendance_estimate",
        "pre_orders",
        "is_breakfast",
        "is_lunch",
        "is_dinner",
    ]
    + [f"item_{item.replace(' ', '_').replace('&', 'and')}" for item in ALL_MENU_ITEMS]
)

TARGET_COLUMN = "meals_prepared"


def _menu_col(item: str) -> str:
    """Return the feature column name for a menu item."""
    return f"item_{item.replace(' ', '_').replace('&', 'and')}"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw records into ML-ready feature DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw meal records (as returned by database.get_all_records()).

    Returns
    -------
    pd.DataFrame
        Feature matrix with columns in FEATURE_COLUMNS order.
    """
    out = df.copy()

    # ── Day-of-week encoded as sine/cosine (cyclical encoding) ────────────────
    # This lets the model understand that Sunday (6) is close to Monday (0).
    out["date"] = pd.to_datetime(out["date"])
    dow = out["date"].dt.dayofweek          # 0 = Monday, 6 = Sunday
    out["dow_sin"] = np.sin(2 * np.pi * dow / 7)
    out["dow_cos"] = np.cos(2 * np.pi * dow / 7)

    # ── Meal period one-hot encoding ──────────────────────────────────────────
    out["is_breakfast"] = (out["meal_period"] == "Breakfast").astype(int)
    out["is_lunch"]     = (out["meal_period"] == "Lunch").astype(int)
    out["is_dinner"]    = (out["meal_period"] == "Dinner").astype(int)

    # ── Menu item one-hot encoding ────────────────────────────────────────────
    for item in ALL_MENU_ITEMS:
        out[_menu_col(item)] = (out["menu_item"] == item).astype(int)

    return out[FEATURE_COLUMNS]
