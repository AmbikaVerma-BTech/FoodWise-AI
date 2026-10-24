"""
src/impact.py
Sustainability impact calculations for FoodWise AI.

All metrics are calculated from recorded data + documented assumptions.
No savings are claimed without a defensible baseline.
Every assumption is passed in as a parameter so it is visible in the UI.
"""

import pandas as pd


def compute_impact_metrics(
    df: pd.DataFrame,
    kg_per_portion: float = 0.35,
    co2_per_kg: float = 2.5,
    cost_per_portion: float = 50.0,
) -> dict:
    """
    Calculate sustainability metrics from meal records.

    Parameters
    ----------
    df : pd.DataFrame
        Meal records.
    kg_per_portion : float
        Assumed average food weight per portion in kg.
        (Documented assumption — adjust in Settings page.)
    co2_per_kg : float
        kg of CO₂ equivalent per kg of food waste.
        Default 2.5 from IPCC mixed food waste figure.
        (Documented assumption — adjust in Settings page.)
    cost_per_portion : float
        Average cost per portion in local currency.
        (Documented assumption — adjust in Settings page.)

    Returns
    -------
    dict with keys:
        total_discarded_portions, total_discarded_kg,
        total_co2e_kg, financial_waste.
    """
    total_discarded = int(df["discarded"].sum())

    total_discarded_kg = total_discarded * kg_per_portion
    total_co2e_kg      = total_discarded_kg * co2_per_kg
    financial_waste    = total_discarded * cost_per_portion

    return {
        "total_discarded_portions": total_discarded,
        "total_discarded_kg":       round(total_discarded_kg, 2),
        "total_co2e_kg":            round(total_co2e_kg, 2),
        "financial_waste":          round(financial_waste, 2),
        # Document every assumption used
        "_assumptions": {
            "kg_per_portion": kg_per_portion,
            "co2_per_kg": co2_per_kg,
            "cost_per_portion": cost_per_portion,
            "note": (
                "Metrics calculated from recorded data only. "
                "No savings claimed without a defensible real-world baseline."
            ),
        },
    }
