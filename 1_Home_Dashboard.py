"""
Page 1 — Home Dashboard
Shows a summary of today's forecast, recent waste, and sustainability metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.database import get_recent_records, get_all_records
from src.ui_styles import page_header

st.set_page_config(page_title="Home Dashboard", page_icon="🏠", layout="wide")
page_header("🏠", "Home Dashboard", "Live summary of canteen performance — synthetic data, clearly labelled.")

# ── Summary metrics ────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
try:
    _df_all = get_all_records()
    _n_records = len(_df_all)
    if _n_records > 0:
        _avg_served = round(
            _df_all.groupby("date")["meals_served"].sum().mean(), 1
        )
        _waste_pct = round(
            _df_all["discarded"].sum() / _df_all["meals_prepared"].sum() * 100, 1
        ) if _df_all["meals_prepared"].sum() > 0 else 0.0
        _sdg_score = max(0.0, min(100.0, round(100.0 - _waste_pct, 1)))
        col1.metric("📋 Records in DB",          f"{_n_records:,}",   help="Total meal records stored")
        col2.metric("🍽️ Avg Meals Served / Day", f"{_avg_served}",    help="Across all records")
        col3.metric("♻️ Avg Waste %",            f"{_waste_pct}%",    help="(Discarded / Prepared) × 100")
        col4.metric("🌱 SDG 12 Score",           f"{_sdg_score}",     help="100 − waste_rate. Higher is better.")
    else:
        col1.metric("📋 Records in DB",          "0",  help="Total meal records stored")
        col2.metric("🍽️ Avg Meals Served / Day", "—",  help="Across all records")
        col3.metric("♻️ Avg Waste %",            "—",  help="(Discarded / Prepared) × 100")
        col4.metric("🌱 SDG 12 Score",           "—",  help="Based on recorded data only")
except Exception:
    col1.metric("📋 Records in DB",          "—", help="Total meal records stored")
    col2.metric("🍽️ Avg Meals Served / Day", "—", help="Across all records")
    col3.metric("♻️ Avg Waste %",            "—", help="(Discarded / Prepared) × 100")
    col4.metric("🌱 SDG 12 Score",           "—", help="Based on recorded data only")

st.markdown("---")

# ── Recent records preview ─────────────────────────────────────────────────────
st.subheader("📊 Recent Meal Records")
try:
    df = get_recent_records(limit=30)   # 30 rows ≈ last 10 days (3 periods/day)
    if df.empty:
        st.info("No records yet. Go to **Data Management** to import the synthetic dataset.")
    else:
        # Show a clean subset of columns in the table
        display_cols = ["date", "meal_period", "menu_item",
                        "meals_prepared", "meals_served", "discarded", "is_synthetic"]
        st.dataframe(df[display_cols].sort_values("date", ascending=False),
                     use_container_width=True, hide_index=True)

        # Aggregate by date so each date shows one grouped bar (not 3 overlapping)
        df_chart = (
            df.groupby("date")[["meals_prepared", "meals_served", "discarded"]]
            .sum()
            .reset_index()
            .sort_values("date")          # ascending → chart reads left→right
        )
        fig = px.bar(
            df_chart,
            x="date",
            y=["meals_prepared", "meals_served", "discarded"],
            barmode="group",
            title="Last 10 Days: Daily Prepared vs Served vs Discarded",
            labels={"value": "Portions", "variable": "Category"},
            color_discrete_map={
                "meals_prepared": "#4f9cf9",
                "meals_served":   "#34d399",
                "discarded":      "#f87171",
            },
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#e8eaf0"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.warning(f"Could not load records: {e}")

st.markdown("---")
st.caption(
    "FoodWise AI · Supports UN SDG 12 · "
    "Synthetic data is for development/testing only and is not real-world evidence."
)
