"""
src/waste.py
Waste calculations for FoodWise AI.
All calculations are from recorded data only.
"""

import pandas as pd


def compute_waste_summary(df: pd.DataFrame) -> dict:
    """
    Compute aggregate waste metrics from a DataFrame of meal records.

    Parameters
    ----------
    df : pd.DataFrame
        Meal records (from database.get_all_records()).

    Returns
    -------
    dict with keys:
        total_prepared, total_served, total_discarded,
        total_leftovers, waste_rate_pct.
    """
    total_prepared  = int(df["meals_prepared"].sum())
    total_served    = int(df["meals_served"].sum())
    total_leftovers = int(df["leftovers"].sum())
    total_discarded = int(df["discarded"].sum())

    waste_rate_pct = (
        (total_discarded / total_prepared * 100) if total_prepared > 0 else 0.0
    )

    return {
        "total_prepared":  total_prepared,
        "total_served":    total_served,
        "total_leftovers": total_leftovers,
        "total_discarded": total_discarded,
        "waste_rate_pct":  round(waste_rate_pct, 2),
    }
