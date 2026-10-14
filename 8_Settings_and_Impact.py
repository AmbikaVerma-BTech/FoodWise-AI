"""
Page 8 — Settings and Impact
Sustainability metrics, ₹ savings, CO₂ avoided, and what-if analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.database import get_all_records
from src.impact import compute_impact_metrics
from src.ui_styles import page_header

st.set_page_config(page_title="Settings & Impact", page_icon="🌍", layout="wide")
page_header("🌍", "Settings & Impact", "Sustainability metrics, ₹ savings, CO₂ avoided — all from recorded data.")

_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(26,31,46,0.6)",
    font=dict(family="Inter", color="#e8eaf0"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

# ── Assumptions panel ──────────────────────────────────────────────────────────
st.subheader("⚙️ Calculation Assumptions")
st.info(
    "All sustainability metrics are calculated **only from recorded data** "
    "using the assumptions below. Changing these values updates the metrics live. "
    "No savings are claimed without a defensible baseline."
)

col1, col2 = st.columns(2)
with col1:
    kg_per_portion = st.number_input(
        "⚖️ Average food weight per portion (kg)", min_value=0.1, max_value=2.0,
        value=0.35, step=0.05,
        help="Used to convert portions to kilograms of food waste.",
    )
    co2_per_kg = st.number_input(
        "🌫️ CO₂e per kg of food waste (kg)", min_value=0.1, max_value=10.0,
        value=2.5, step=0.1,
        help="IPCC default for mixed food waste. Adjust to your local figure.",
    )
with col2:
    cost_per_portion = st.number_input(
        "💰 Average cost per portion (₹)", min_value=0.0, value=50.0, step=5.0,
        help="Used to estimate financial waste. Set to your canteen's actual cost.",
    )
    currency_label = st.text_input("🏷️ Currency label", value="₹")

st.markdown("---")

# ── Impact metrics ─────────────────────────────────────────────────────────────
st.subheader("📊 Impact Metrics (from recorded data)")

try:
    df = get_all_records()
    if df.empty:
        st.info("No records yet. Import data on the Data Management page.")
    else:
        if "is_synthetic" in df.columns and df["is_synthetic"].any():
            st.warning(
                "⚠️ Some or all records are **synthetic**. "
                "Metrics shown here are illustrative only — not real-world evidence."
            )

        metrics = compute_impact_metrics(
            df,
            kg_per_portion=kg_per_portion,
            co2_per_kg=co2_per_kg,
            cost_per_portion=cost_per_portion,
        )

        total_prepared  = int(df["meals_prepared"].sum())
        total_discarded = metrics["total_discarded_portions"]
        total_served    = int(df["meals_served"].sum())

        # ── Headline numbers ───────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "🗑️ Total Food Wasted",
            f"{metrics['total_discarded_kg']:.1f} kg",
            help="Discarded portions × kg_per_portion.",
        )
        c2.metric(
            "🌫️ CO₂e from Waste",
            f"{metrics['total_co2e_kg']:.1f} kg CO₂e",
            help=f"Food waste kg × {co2_per_kg} kg CO₂e/kg.",
        )
        c3.metric(
            "💸 Financial Waste",
            f"{currency_label} {metrics['financial_waste']:,.0f}",
            help=f"Discarded portions × {cost_per_portion} {currency_label}/portion.",
        )
        c4.metric(
            "✅ Meals Successfully Served",
            f"{total_served:,}",
            help="Total portions actually given to students.",
        )

        st.markdown("---")

        # ── ₹ Savings & CO₂ avoided section ───────────────────────────────────
        st.subheader("💡 Potential Savings if Waste is Reduced")
        st.markdown(
            "Use the slider below to estimate how much money and CO₂ you could save "
            "by reducing food waste by a target percentage."
        )

        target_reduction = st.slider(
            "🎯 Target waste reduction (%)",
            min_value=10, max_value=90, value=50, step=10,
            help="What % of current food waste could you eliminate?",
        )

        saved_portions = int(total_discarded * target_reduction / 100)
        saved_kg       = round(saved_portions * kg_per_portion, 1)
        saved_co2      = round(saved_kg * co2_per_kg, 1)
        saved_money    = round(saved_portions * cost_per_portion, 0)

        s1, s2, s3 = st.columns(3)
        s1.metric(
            f"🍱 Portions Saved ({target_reduction}% reduction)",
            f"{saved_portions:,}",
            help="Portions no longer discarded.",
        )
        s2.metric(
            "💰 Money Saved",
            f"{currency_label} {saved_money:,.0f}",
            help=f"Saved portions × {cost_per_portion} {currency_label}/portion.",
        )
        s3.metric(
            "🌱 CO₂e Avoided",
            f"{saved_co2:.1f} kg CO₂e",
            help=f"Saved food kg × {co2_per_kg} kg CO₂e/kg.",
        )

        st.markdown("---")

        # ── What-if attendance slider ──────────────────────────────────────────
        st.subheader("🔮 What-If Analysis: Attendance Change")
        st.markdown(
            "Simulate how a change in attendance affects estimated waste and cost."
        )
        avg_attendance = int(df["attendance_estimate"].mean()) if "attendance_estimate" in df.columns else 300
        whatif_pct = st.slider(
            "📈 Change in attendance (%)",
            min_value=-50, max_value=50, value=0, step=5,
            help="Negative = fewer students. Positive = more students.",
            format="%d%%",
        )
        scale = 1 + whatif_pct / 100
        wi_discarded  = int(total_discarded * scale)
        wi_waste_kg   = round(wi_discarded * kg_per_portion, 1)
        wi_cost       = round(wi_discarded * cost_per_portion, 0)
        wi_co2        = round(wi_waste_kg * co2_per_kg, 1)

        w1, w2, w3 = st.columns(3)
        w1.metric(
            "🗑️ Projected Discarded Portions",
            f"{wi_discarded:,}",
            delta=f"{wi_discarded - total_discarded:+,} vs current",
        )
        w2.metric(
            "💸 Projected Financial Waste",
            f"{currency_label} {wi_cost:,.0f}",
            delta=f"{currency_label} {wi_cost - metrics['financial_waste']:+,.0f} vs current",
        )
        w3.metric(
            "🌫️ Projected CO₂e",
            f"{wi_co2:.1f} kg",
            delta=f"{wi_co2 - metrics['total_co2e_kg']:+.1f} kg vs current",
        )

        st.markdown("---")

        # ── Monthly trend ──────────────────────────────────────────────────────
        st.subheader("📅 Monthly Waste Trend")
        df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
        monthly = df.groupby("month").agg(
            discarded=("discarded", "sum"),
            prepared=("meals_prepared", "sum"),
        ).reset_index()
        monthly["waste_pct"] = (monthly["discarded"] / monthly["prepared"] * 100).round(1)

        tab1, tab2 = st.tabs(["Discarded Portions", "Waste Rate %"])
        with tab1:
            fig1 = px.line(
                monthly, x="month", y="discarded",
                title="Monthly Discarded Portions",
                labels={"discarded": "Discarded Portions", "month": "Month"},
                markers=True, color_discrete_sequence=["#f87171"],
            )
            fig1.update_layout(**_LAYOUT)
            st.plotly_chart(fig1, use_container_width=True)
        with tab2:
            fig2 = px.line(
                monthly, x="month", y="waste_pct",
                title="Monthly Waste Rate (%)",
                labels={"waste_pct": "Waste %", "month": "Month"},
                markers=True, color_discrete_sequence=["#4f9cf9"],
            )
            fig2.update_layout(**_LAYOUT)
            st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"Error loading impact metrics: {e}")

st.markdown("---")
st.subheader("🌱 UN SDG 12 — Responsible Consumption and Production")
st.markdown(
    "This app supports **SDG 12.3**: By 2030, halve per capita global food waste "
    "at the retail and consumer levels and reduce food losses along production and "
    "supply chains, including post-harvest losses.\n\n"
    "_Source: United Nations Sustainable Development Goals_"
)

st.markdown("---")
st.caption(
    "FoodWise AI · All metrics calculated from recorded data + documented assumptions · "
    "No savings claimed without a defensible baseline."
)
