"""
Page 3 — Preparation Planner
Shows the forecast, uncertainty range, risk flags, food-safety reminders,
and a downloadable daily prep sheet for canteen staff.
The final preparation quantity is always decided by canteen staff.
"""

import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.forecast import generate_forecast
from src.features import ALL_MENU_ITEMS
from src.ui_styles import page_header

st.set_page_config(page_title="Preparation Planner", page_icon="📋", layout="wide")
page_header("📋", "Preparation Planner", "Model suggestions only — final decision is always made by canteen staff.")

# ── Food Safety Reminder (always visible) ──────────────────────────────────────
st.error(
    "🛑 **Food Safety Reminder**\n\n"
    "• Cooked food must be served within **2 hours** at room temperature.\n"
    "• Store excess food below **5 °C** (refrigerator) or above **60 °C** (hot-hold).\n"
    "• Never re-serve food that has been left out for more than 2 hours.\n"
    "• Label all stored food with the date and time of preparation.\n"
    "• When in doubt, discard — food safety comes first."
)

st.markdown("---")

# ── Planner Inputs ─────────────────────────────────────────────────────────────
st.subheader("⚙️ Plan Your Preparation")
col1, col2, col3 = st.columns(3)
with col1:
    plan_date = st.date_input("📅 Date to plan for")
with col2:
    meal_period = st.selectbox("🍴 Meal Period", ["Breakfast", "Lunch", "Dinner"])
with col3:
    menu_item = st.selectbox("🥘 Menu Item", ALL_MENU_ITEMS)

col_l, col_r = st.columns(2)
with col_l:
    is_special = st.checkbox("🎉 Special event on this day?")
    attendance = st.slider("👥 Expected attendance", 50, 1000, 300, 10)
with col_r:
    buffer_pct = st.slider(
        "🛡️ Safety buffer % (extra above forecast)",
        min_value=0, max_value=30, value=10, step=5,
        help="Higher buffer = less risk of running out, but more potential waste.",
    )

st.markdown("")
if st.button("🚀 Generate Preparation Plan", type="primary", use_container_width=True):
    with st.spinner("Calculating…"):
        try:
            result = generate_forecast(
                date=str(plan_date),
                meal_period=meal_period,
                menu_item=menu_item,
                is_special_event=int(is_special),
                attendance_estimate=attendance,
            )
            suggested = int(result["forecast"] * (1 + buffer_pct / 100))

            st.markdown("---")
            st.subheader("📊 Preparation Recommendation")

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("🎯 Model Forecast",    f"{result['forecast']} portions")
            col_b.metric(
                "🛡️ With Buffer",
                f"{suggested} portions",
                help=f"Forecast + {buffer_pct}% safety buffer",
            )
            col_c.metric(
                "📊 Uncertainty Range",
                f"{result['lower']}–{result['upper']}",
                help="Heuristic range — NOT a calibrated probability interval.",
            )

            if result.get("risk_flags"):
                st.warning(
                    "**⚠️ Risk Flags** — indicators only, use your own judgement:\n\n"
                    + "\n\n".join(f"• {f}" for f in result["risk_flags"])
                )

            st.info(
                f"**✅ Suggested preparation: {suggested} portions of {menu_item} "
                f"for {meal_period} on {plan_date}**\n\n"
                "_This is a suggestion only. Canteen staff make the final decision._"
            )

            # ── Downloadable daily prep sheet ──────────────────────────────────
            st.markdown("---")
            st.subheader("⬇️ Daily Prep Sheet")

            prep_data = {
                "Field": [
                    "Date", "Meal Period", "Menu Item", "Expected Attendance",
                    "Special Event", "Model Forecast (portions)",
                    f"With {buffer_pct}% Safety Buffer (portions)",
                    "Lower Estimate", "Upper Estimate",
                    "Model Used", "Note",
                ],
                "Value": [
                    str(plan_date), meal_period, menu_item, attendance,
                    "Yes" if is_special else "No",
                    result["forecast"], suggested,
                    result["lower"], result["upper"],
                    result["model_name"],
                    "Forecast is a model suggestion. Final quantity decided by canteen staff.",
                ],
            }
            prep_df = pd.DataFrame(prep_data)
            st.dataframe(prep_df, use_container_width=True, hide_index=True)

            csv_bytes = prep_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Prep Sheet as CSV",
                data=csv_bytes,
                file_name=f"prep_sheet_{plan_date}_{meal_period.lower()}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        except FileNotFoundError:
            st.error("❌ No trained model found. Train a model on the Model Performance page first.")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.caption(
    "FoodWise AI · Risk flags are indicators only, not calibrated probabilities · "
    "Final preparation decisions rest with canteen staff."
)
