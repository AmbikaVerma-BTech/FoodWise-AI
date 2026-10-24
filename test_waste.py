"""
tests/test_waste.py
Unit tests for src/waste.py and src/impact.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import pytest
from src.waste import compute_waste_summary
from src.impact import compute_impact_metrics


def _sample_df():
    return pd.DataFrame(
        {
            "meals_prepared": [100, 200, 150],
            "meals_served":   [90,  180, 140],
            "leftovers":      [10,  20,  10],
            "discarded":      [5,   10,  8],
        }
    )


# ── waste.py tests ────────────────────────────────────────────────────────────

def test_total_prepared():
    df = _sample_df()
    s = compute_waste_summary(df)
    assert s["total_prepared"] == 450


def test_total_discarded():
    df = _sample_df()
    s = compute_waste_summary(df)
    assert s["total_discarded"] == 23


def test_waste_rate():
    df = _sample_df()
    s = compute_waste_summary(df)
    expected = round(23 / 450 * 100, 2)
    assert s["waste_rate_pct"] == expected


def test_waste_rate_zero_prepared():
    df = pd.DataFrame(
        {"meals_prepared": [0], "meals_served": [0],
         "leftovers": [0], "discarded": [0]}
    )
    s = compute_waste_summary(df)
    assert s["waste_rate_pct"] == 0.0


# ── impact.py tests ───────────────────────────────────────────────────────────

def test_impact_discarded_kg():
    df = _sample_df()
    m = compute_impact_metrics(df, kg_per_portion=0.35, co2_per_kg=2.5,
                                cost_per_portion=50.0)
    assert m["total_discarded_kg"] == pytest.approx(23 * 0.35, rel=1e-3)


def test_impact_co2():
    df = _sample_df()
    m = compute_impact_metrics(df, kg_per_portion=0.35, co2_per_kg=2.5,
                                cost_per_portion=50.0)
    assert m["total_co2e_kg"] == pytest.approx(23 * 0.35 * 2.5, rel=1e-3)


def test_impact_financial():
    df = _sample_df()
    m = compute_impact_metrics(df, kg_per_portion=0.35, co2_per_kg=2.5,
                                cost_per_portion=50.0)
    assert m["financial_waste"] == pytest.approx(23 * 50.0, rel=1e-3)


def test_assumptions_documented():
    df = _sample_df()
    m = compute_impact_metrics(df)
    assert "_assumptions" in m
    assert "note" in m["_assumptions"]
