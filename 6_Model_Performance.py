"""
Page 6 — Model Performance
Train models, compare scores (MAE, RMSE, WAPE), view feature importance,
and see how the best model beats a naive baseline.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.database import get_all_records
from src.models import train_and_evaluate_all, load_model_results
from src.ui_styles import page_header

st.set_page_config(page_title="Model Performance", page_icon="🤖", layout="wide")
page_header("🤖", "Model Performance", "Train models and compare accuracy — best model vs naive baseline.")

_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(26,31,46,0.6)",
    font=dict(family="Inter", color="#e8eaf0"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

# ── Train button ───────────────────────────────────────────────────────────────
st.subheader("🚀 Train Models")
st.info(
    "Training uses a **chronological 80/20 split** — first 80% of dates for training, "
    "last 20% for testing. No shuffling — this prevents data leakage."
)

if st.button("🚀 Train All Models", type="primary", use_container_width=True):
    with st.spinner("Training… this may take a moment."):
        try:
            df = get_all_records()
            if df.empty or len(df) < 20:
                st.error(
                    "Not enough records to train. "
                    "Import the synthetic dataset first (Data Management page). "
                    "Need at least 20 records."
                )
            else:
                results = train_and_evaluate_all(df)
                st.success(f"✅ Training complete! Best model: **{results['best_model']}**")
                st.session_state["model_results"] = results
        except Exception as e:
            st.error(f"Training failed: {e}")

# ── Show results ───────────────────────────────────────────────────────────────
results = st.session_state.get("model_results") or load_model_results()

if results:
    st.markdown("---")

    # ── Headline: does the ML actually beat the baseline? ─────────────────────
    metrics_df = pd.DataFrame(results["metrics"])
    baseline_row = metrics_df[metrics_df["model"] == "Naive Baseline"]
    best_row     = metrics_df[metrics_df["model"] == results["best_model"]]

    # b_mae is needed both inside and outside the headline block
    b_mae = baseline_row["MAE"].values[0] if not baseline_row.empty else None

    if b_mae is not None and not best_row.empty:
        ml_mae = best_row["MAE"].values[0]
        improvement = round((b_mae - ml_mae) / b_mae * 100, 1) if b_mae > 0 else 0.0

        st.subheader("🏆 Does ML beat the Naive Baseline?")
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Naive Baseline MAE",
            f"{b_mae:.1f} portions",
            help="Mean Absolute Error when predicting the training-set average every time.",
        )
        c2.metric(
            f"{results['best_model']} MAE",
            f"{ml_mae:.1f} portions",
            delta=f"-{b_mae - ml_mae:.1f} vs baseline",
            delta_color="normal",
            help="Lower is better.",
        )
        c3.metric(
            "MAE Improvement over Baseline",
            f"{improvement}%",
            help="How much better the best ML model is than simply predicting the mean.",
        )

        if improvement > 0:
            st.success(
                f"✅ **{results['best_model']}** reduces prediction error by **{improvement}%** "
                f"over the naive baseline — the ML model adds real value."
            )
        else:
            st.warning(
                "⚠️ The ML model does not outperform the naive baseline on this dataset. "
                "Try adding more records or real-world data."
            )

    st.markdown("---")
    st.subheader("📊 Full Model Comparison")
    st.dataframe(metrics_df, use_container_width=True)

    # ── Bar chart — all models ─────────────────────────────────────────────────
    fig = px.bar(
        metrics_df,
        x="model",
        y=["MAE", "RMSE", "WAPE"],
        barmode="group",
        title="Model Comparison: MAE, RMSE, WAPE (lower is better)",
        labels={"value": "Score", "variable": "Metric"},
        color_discrete_sequence=["#4f9cf9", "#a78bfa", "#34d399"],
    )
    fig.update_layout(**_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    # ── MAE improvement waterfall ──────────────────────────────────────────────
    if b_mae is not None:
        st.subheader("📉 MAE vs Naive Baseline (per model)")
        mae_df = metrics_df.copy()
        mae_df["vs_baseline"] = b_mae - mae_df["MAE"]
        mae_df["color"] = mae_df["vs_baseline"].apply(
            lambda x: "#34d399" if x > 0 else "#f87171"
        )
        fig_cmp = go.Figure()
        fig_cmp.add_bar(
            x=mae_df["model"],
            y=mae_df["vs_baseline"],
            marker_color=mae_df["color"].tolist(),
            text=mae_df["vs_baseline"].apply(lambda v: f"{v:+.1f}"),
            textposition="outside",
            textfont=dict(color="#e8eaf0"),
        )
        fig_cmp.add_hline(y=0, line_dash="dash", line_color="#8b9cc8")
        fig_cmp.update_layout(
            title="MAE reduction vs Naive Baseline (positive = better than baseline)",
            yaxis_title="MAE improvement (portions)",
            xaxis_title="",
            **_LAYOUT,
        )
        st.plotly_chart(fig_cmp, use_container_width=True)

    st.subheader(f"🏆 Best Model: {results['best_model']}")
    st.caption(
        f"Train size: {results['train_size']} records · "
        f"Test size: {results['test_size']} records · "
        f"Split: chronological (no data leakage)"
    )

    if results.get("feature_importance"):
        st.subheader("🔍 Feature Importance (best model)")
        fi_df = pd.DataFrame(
            results["feature_importance"], columns=["feature", "importance"]
        ).sort_values("importance", ascending=False).head(15)
        fig2 = px.bar(
            fi_df, x="importance", y="feature", orientation="h",
            title="Top 15 Features by Importance",
            labels={"importance": "Importance", "feature": ""},
            color="importance",
            color_continuous_scale=["#1e2538", "#4f9cf9"],
        )
        fig2.update_layout(**_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    st.warning(
        "⚠️ **Limitation:** These scores are from a synthetic dataset. "
        "They demonstrate that the pipeline works, but cannot be used as "
        "real-world performance evidence. Replace with real canteen data "
        "for meaningful results."
    )
else:
    st.info("No model trained yet. Click **Train All Models** above.")

st.markdown("---")
st.caption(
    "FoodWise AI · Chronological split · "
    "Scores from actual evaluation only · No invented confidence values."
)
