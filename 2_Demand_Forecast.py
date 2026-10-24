"""
Page 2 — Demand Forecast
Shows model predictions for a selected date and meal period.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.forecast import generate_forecast
from src.features import ALL_MENU_ITEMS
from src.ui_styles import page_header

st.set_page_config(page_title="Demand Forecast", page_icon="📈", layout="wide")
page_header("📈", "Demand Forecast", "Model-based portion forecasts — estimates only, always review before acting.")

# ── Inputs ─────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    forecast_date = st.date_input("📅 Forecast Date")
with col2:
    meal_period = st.selectbox("🍴 Meal Period", ["Breakfast", "Lunch", "Dinner"])
with col3:
    menu_item = st.selectbox("🥘 Menu Item", ALL_MENU_ITEMS)

col_l, col_r = st.columns(2)
with col_l:
    is_special = st.checkbox("🎉 Special event on this day? (exam, sports day, holiday…)")
with col_r:
    attendance = st.slider(
        "👥 Expected student attendance", min_value=50, max_value=1000, value=300, step=10
    )

st.markdown("")
if st.button("🚀 Generate Forecast", type="primary", use_container_width=True):
    with st.spinner("Running model…"):
        try:
            result = generate_forecast(
                date=str(forecast_date),
                meal_period=meal_period,
                menu_item=menu_item,
                is_special_event=int(is_special),
                attendance_estimate=attendance,
            )
            st.success("✅ Forecast generated!")
            st.markdown("---")

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("🎯 Point Forecast",    f"{result['forecast']} portions")
            col_b.metric(
                "📊 Uncertainty Range",
                f"{result['lower']}–{result['upper']} portions",
                help="Heuristic ±1 residual std — NOT a calibrated probability interval.",
            )
            col_c.metric("🤖 Model Used", result["model_name"])

            if result.get("risk_flags"):
                st.warning(
                    "**⚠️ Risk Flags** — indicators only, not probabilities:\n\n"
                    + "\n\n".join(f"• {f}" for f in result["risk_flags"])
                )

            # ── Chart ──────────────────────────────────────────────────────────
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Lower estimate", "Point forecast", "Upper estimate"],
                y=[result["lower"], result["forecast"], result["upper"]],
                marker_color=["#a78bfa", "#4f9cf9", "#a78bfa"],
                marker_line_color=["#7c5cd8", "#2563eb", "#7c5cd8"],
                marker_line_width=2,
                text=[result["lower"], result["forecast"], result["upper"]],
                textposition="auto",
                textfont=dict(size=16, color="#ffffff", family="Inter"),
            ))
            fig.update_layout(
                title=dict(text="Forecast with Uncertainty Range", font=dict(size=18, color="#e8eaf0")),
                yaxis_title="Portions",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(26,31,46,0.6)",
                font=dict(family="Inter", color="#e8eaf0"),
            )
            st.plotly_chart(fig, use_container_width=True)

        except FileNotFoundError:
            st.error("❌ No trained model found. Go to **Model Performance** to train a model first.")
        except Exception as e:
            st.error(f"Forecast error: {e}")

st.markdown("---")
st.caption(
    "FoodWise AI · Forecasts are estimates based on synthetic training data · "
    "Final decisions remain with canteen staff."
)
