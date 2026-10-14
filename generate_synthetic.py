"""
src/generate_synthetic.py
Generates a clearly-labelled synthetic canteen dataset.

⚠️  SYNTHETIC DATA NOTICE
This data is computer-generated using realistic statistical patterns.
Every row is labelled is_synthetic = 1.
It is NOT real-world evidence and must never be presented as such.
It is intended for development, testing, and demonstration only.
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta

# ── Fixed menu lists (one list per meal period) ───────────────────────────────
BREAKFAST_ITEMS = [
    "Idli & Sambar",
    "Poha",
    "Bread & Omelette",
    "Upma",
    "Paratha",
]

LUNCH_ITEMS = [
    "Rice & Curry",
    "Dal & Roti",
    "Fried Rice",
    "Noodles",
    "Pasta",
]

DINNER_ITEMS = [
    "Rice & Curry",
    "Soup",
    "Sandwich",
    "Salad Bowl",
    "Dal & Roti",
]

MEAL_PERIODS = ["Breakfast", "Lunch", "Dinner"]

# Base demand per meal period (approximate portions per day at full attendance)
BASE_DEMAND = {"Breakfast": 120, "Lunch": 250, "Dinner": 180}

# Day-of-week multipliers (Monday=0 … Sunday=6)
DOW_MULTIPLIER = {0: 1.0, 1: 1.0, 2: 1.05, 3: 1.1, 4: 1.15, 5: 0.6, 6: 0.4}

# Special event: college festival, exam, sports day (roughly 10% of days)
SPECIAL_EVENT_PROB = 0.10
SPECIAL_EVENT_MULTIPLIER = 1.3

# Waste parameters
WASTE_RATE_MEAN = 0.08   # 8% of prepared portions are discarded on average
WASTE_RATE_STD  = 0.04


def generate_synthetic_data(n_days: int = 365, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic canteen meal records.

    Parameters
    ----------
    n_days : int
        Number of calendar days to generate (one row per meal period per day).
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Clearly-labelled synthetic dataset (is_synthetic = 1 for every row).
    """
    rng = np.random.default_rng(seed)
    start_date = date(2023, 1, 1)
    rows = []

    for day_offset in range(n_days):
        current_date = start_date + timedelta(days=day_offset)
        dow = current_date.weekday()          # 0 = Monday
        dow_mult = DOW_MULTIPLIER[dow]

        # ~10% of days are special events
        is_special = int(rng.random() < SPECIAL_EVENT_PROB)
        special_mult = SPECIAL_EVENT_MULTIPLIER if is_special else 1.0

        # Attendance: 200–600 students, lower on weekends.
        # Ensure low < high regardless of base_att value.
        base_att = 400 if dow < 5 else 150
        att_low  = max(50, base_att - 80)
        att_high = max(att_low + 1, base_att + 80)
        attendance = int(rng.integers(att_low, att_high))

        for period in MEAL_PERIODS:
            if period == "Breakfast":
                items = BREAKFAST_ITEMS
            elif period == "Lunch":
                items = LUNCH_ITEMS
            else:
                items = DINNER_ITEMS

            # Pick a random menu item for this meal
            menu_item = rng.choice(items)

            # Base demand scaled by attendance, day of week, and special events
            att_fraction = attendance / 400
            base = BASE_DEMAND[period] * dow_mult * special_mult * att_fraction
            noise = rng.normal(0, base * 0.10)
            meals_ordered = max(0, int(round(base + noise)))

            # Pre-orders: ~20% of orders placed in advance
            pre_orders = int(rng.binomial(meals_ordered, 0.20))

            # Prepared: slightly more than ordered (safety buffer ~5–15%)
            buffer = rng.uniform(1.05, 1.15)
            meals_prepared = max(meals_ordered, int(round(meals_ordered * buffer)))

            # Served: at most what was prepared
            serve_fraction = rng.uniform(0.80, 1.00)
            meals_served = min(meals_prepared, int(round(meals_ordered * serve_fraction)))

            # Leftovers and discarded
            leftovers = meals_prepared - meals_served
            waste_rate = max(0.0, rng.normal(WASTE_RATE_MEAN, WASTE_RATE_STD))
            discarded = min(leftovers, int(round(meals_prepared * waste_rate)))

            rows.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day_of_week": current_date.strftime("%A"),
                    "meal_period": period,
                    "menu_item": menu_item,
                    "is_special_event": is_special,
                    "attendance_estimate": attendance,
                    "pre_orders": pre_orders,
                    "meals_ordered": meals_ordered,
                    "meals_prepared": meals_prepared,
                    "meals_served": meals_served,
                    "leftovers": leftovers,
                    "discarded": discarded,
                    "is_synthetic": 1,  # Always 1 — transparency flag
                }
            )

    df = pd.DataFrame(rows)
    return df
