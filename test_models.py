"""
tests/test_models.py
Unit tests for src/models.py  (training + evaluation pipeline).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
import pytest
from src.generate_synthetic import generate_synthetic_data
from src.models import train_and_evaluate_all, load_model_results, _wape


def _small_df():
    """Generate a small synthetic dataset for fast testing."""
    return generate_synthetic_data(n_days=60, seed=0)


def test_train_returns_metrics():
    df = _small_df()
    results = train_and_evaluate_all(df)
    assert "metrics" in results
    assert len(results["metrics"]) == 4  # baseline + 3 models


def test_all_metrics_present():
    df = _small_df()
    results = train_and_evaluate_all(df)
    for row in results["metrics"]:
        assert "MAE" in row
        assert "RMSE" in row
        assert "WAPE" in row


def test_best_model_key_present():
    df = _small_df()
    results = train_and_evaluate_all(df)
    assert "best_model" in results
    assert isinstance(results["best_model"], str)


def test_chronological_split_sizes():
    df = _small_df()
    results = train_and_evaluate_all(df)
    total = results["train_size"] + results["test_size"]
    assert total == len(df)
    assert results["train_size"] == int(len(df) * 0.80)


def test_wape_zero_actual():
    """WAPE should return nan when all actuals are zero."""
    result = _wape(np.zeros(5), np.ones(5))
    assert np.isnan(result)


def test_wape_perfect_forecast():
    """WAPE should be 0 for a perfect forecast."""
    y = np.array([100.0, 200.0, 150.0])
    result = _wape(y, y)
    assert result == pytest.approx(0.0)
