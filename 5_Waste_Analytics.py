"""
Page 5 — Waste Analytics
Tracks prepared, served, leftover, and discarded quantities separately.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.database import get_all_records
from src.waste import compute_waste_summary
from src.ui_styles import page_header

st.set_page_config(page_title="Waste Analytics", page_icon="♻️", layout="wide")
page_header("♻️", "Waste Analytics", "All metrics from recorded data only — no savings claimed without a baseline.")

_CHART_COLORS = {
    "meals_prepared": "#4f9cf9",
    "meals_served":   "#34d399",
    "discarded":      "#f87171",
}
_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(26,31,46,0.6)",
    font=dict(family="Inter", color="#e8eaf0"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

try:
    df = get_all_records()
    if df.empty:
        st.info("No records yet. Import data on the Data Management page.")
    else:
        if "is_synthetic" in df.columns and df["is_synthetic"].any():
            st.warning(
                "⚠️ Some or all records are **synthetic** (is_synthetic = 1). "
                "Metrics shown here are for demonstration only — not real-world evidence."
            )

        summary = compute_waste_summary(df)

        # ── Top metrics ────────────────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🍱 Total Prepared",  f"{summary['total_prepared']:,} portions")
        col2.metric("✅ Total Served",    f"{summary['total_served']:,} portions")
        col3.metric("🗑️ Total Discarded", f"{summary['total_discarded']:,} portions")
        col4.metric(
            "📉 Waste Rate",
            f"{summary['waste_rate_pct']:.1f}%",
            help="(Total discarded / Total prepared) × 100. Calculated from recorded data only.",
        )

        st.markdown("---")

        # ── Waste over time ────────────────────────────────────────────────────
        st.subheader("📅 Waste Over Time")
        daily = (
            df.groupby("date")[["meals_prepared", "meals_served", "discarded"]]
            .sum()
            .reset_index()
        )
        fig1 = px.line(
            daily,
            x="date",
            y=["meals_prepared", "meals_served", "discarded"],
            title="Daily: Prepared vs Served vs Discarded",
            labels={"value": "Portions", "variable": "Category"},
            color_discrete_map=_CHART_COLORS,
            markers=True,
        )
        fig1.update_layout(**_LAYOUT)
        st.plotly_chart(fig1, use_container_width=True)

        # ── By meal period ─────────────────────────────────────────────────────
        st.subheader("🍴 Waste by Meal Period")
        period_df = (
            df.groupby("meal_period")[["meals_prepared", "meals_served", "discarded"]]
            .sum()
            .reset_index()
        )
        fig2 = px.bar(
            period_df,
            x="meal_period",
            y=["meals_prepared", "meals_served", "discarded"],
            barmode="group",
            title="Prepared vs Served vs Discarded by Meal Period",
            labels={"value": "Portions", "variable": "Category"},
            color_discrete_map=_CHART_COLORS,
        )
        fig2.update_layout(**_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

        # ── By menu item ───────────────────────────────────────────────────────
        st.subheader("🥘 Waste by Menu Item")
        item_df = (
            df.groupby("menu_item")["discarded"].sum().reset_index()
            .sort_values("discarded", ascending=False)
        )
        fig3 = px.bar(
            item_df,
            x="menu_item",
            y="discarded",
            title="Total Discarded Portions by Menu Item",
            labels={"discarded": "Discarded Portions"},
            color="discarded",
            color_continuous_scale=["#1e2538", "#f87171"],
        )
        fig3.update_layout(**_LAYOUT)
        st.plotly_chart(fig3, use_container_width=True)

except Exception as e:
    st.error(f"Error loading analytics: {e}")

st.markdown("---")
st.caption(
    "FoodWise AI · Waste Rate = Discarded ÷ Prepared · "
    "No savings claimed without a defensible baseline."
)
