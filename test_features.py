"""
tests/test_features.py
Unit tests for src/features.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
import pytest
from src.features import build_features, FEATURE_COLUMNS


def _sample_df():
    return pd.DataFrame(
        {
            "date": ["2023-01-02", "2023-01-02", "2023-01-07"],
            "meal_period": ["Breakfast", "Lunch", "Dinner"],
            "menu_item": ["Idli & Sambar", "Rice & Curry", "Soup"],
            "is_special_event": [0, 1, 0],
            "attendance_estimate": [300, 400, 200],
            "pre_orders": [10, 20, 5],
            "meals_prepared": [120, 250, 160],
        }
    )


def test_build_features_returns_correct_columns():
    df = _sample_df()
    X = build_features(df)
    assert list(X.columns) == FEATURE_COLUMNS


def test_build_features_no_nulls():
    df = _sample_df()
    X = build_features(df)
    assert X.isnull().sum().sum() == 0


def test_dow_encoding_is_cyclical():
    df = _sample_df()
    X = build_features(df)
    # sin^2 + cos^2 should equal 1 for each row
    vals = X["dow_sin"].values ** 2 + X["dow_cos"].values ** 2
    np.testing.assert_allclose(vals, np.ones(len(vals)), atol=1e-6)


def test_meal_period_one_hot():
    df = _sample_df()
    X = build_features(df)
    assert X.loc[0, "is_breakfast"] == 1
    assert X.loc[1, "is_lunch"] == 1
    assert X.loc[2, "is_dinner"] == 1


def test_menu_item_one_hot():
    df = _sample_df()
    X = build_features(df)
    # Row 0: Idli & Sambar → item_Idli_and_Sambar = 1
    assert X.loc[0, "item_Idli_and_Sambar"] == 1
    # Row 1: Rice & Curry → item_Rice_and_Curry = 1
    assert X.loc[1, "item_Rice_and_Curry"] == 1
    # Row 2: Soup → item_Soup = 1
    assert X.loc[2, "item_Soup"] == 1
    # Each row must have exactly one menu-item flag set
    from src.features import ALL_MENU_ITEMS, _menu_col
    menu_cols = [_menu_col(i) for i in ALL_MENU_ITEMS]
    assert (X[menu_cols].sum(axis=1) == 1).all()
