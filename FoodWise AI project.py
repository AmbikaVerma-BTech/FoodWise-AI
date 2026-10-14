"""
FoodWise AI — Main Entry Point
Run with: streamlit run app.py

Auto-seeding behaviour
----------------------
On first run (empty database) this entry point automatically:
  1. Loads the bundled synthetic CSV into the database.
  2. Trains all models and saves the best one.
This means the app is fully functional on every cold start — including
cloud deployments where the filesystem is ephemeral (e.g. Streamlit
Community Cloud).
"""

import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(__file__))

from src.database import get_all_records, bulk_insert_from_df
from src.models import train_and_evaluate_all
from src.ui_styles import inject_styles

# ── Path to the bundled seed CSV ──────────────────────────────────────────────
_SEED_CSV = os.path.join(os.path.dirname(__file__), "data", "synthetic", "synthetic_365.csv")
_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
_MODEL_FILE = os.path.join(_MODEL_DIR, "best_model.joblib")

st.set_page_config(
    page_title="FoodWise AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()


# ── Auto-seed: runs silently on every cold start ──────────────────────────────
@st.cache_resource(show_spinner=False)
def _auto_seed():
    """
    Seed the database and train a model if neither exists yet.
    Uses st.cache_resource so it runs exactly once per server process,
    not once per user session.

    Seeding strategy (in priority order):
      1. Load from the bundled CSV at data/synthetic/synthetic_365.csv
         (fast, deterministic, no computation needed).
      2. If the CSV is missing, generate 365 days of synthetic data
         in-memory and also write the CSV for future starts.

    Returns a list of status strings shown in the sidebar startup log.
    """
    import pandas as pd
    from src.generate_synthetic import generate_synthetic_data

    messages = []

    # 1 ── Seed database from CSV (or generate) if database is empty
    try:
        df_existing = get_all_records()
    except Exception:
        df_existing = None

    db_was_empty = df_existing is None or df_existing.empty

    if db_was_empty:
        try:
            if os.path.exists(_SEED_CSV):
                df_seed = pd.read_csv(_SEED_CSV)
            else:
                # CSV not bundled — generate in-memory and save for next time
                df_seed = generate_synthetic_data(n_days=365, seed=42)
                os.makedirs(os.path.dirname(_SEED_CSV), exist_ok=True)
                df_seed.to_csv(_SEED_CSV, index=False)
            bulk_insert_from_df(df_seed)
            messages.append(f"Auto-loaded {len(df_seed)} synthetic records.")
        except Exception as exc:
            messages.append(f"Auto-seed failed: {exc}")

    # 2 ── Train model if no saved model exists
    if not os.path.exists(_MODEL_FILE):
        try:
            df_for_train = get_all_records()
            if not df_for_train.empty and len(df_for_train) >= 20:
                results = train_and_evaluate_all(df_for_train)
                messages.append(
                    f"Auto-trained model. Best: {results['best_model']}."
                )
        except Exception as exc:
            messages.append(f"Auto-train failed: {exc}")

    return messages


_seed_messages = _auto_seed()

# ── Landing page metrics (computed from live DB) ──────────────────────────────
import pandas as pd
from src.waste import compute_waste_summary
from src.models import load_model_results as _load_results

def _landing_metrics():
    """Return (forecast_today, waste_reduction_pct, sdg_score) from the DB."""
    try:
        df = get_all_records()
        if df.empty:
            return None, None, None
        summary  = compute_waste_summary(df)
        waste_pct = summary["waste_rate_pct"]
        sdg_score = round(max(0.0, min(100.0, 100.0 - waste_pct)), 1)

        # Meals forecast today: avg meals served per day across all records
        avg_served = round(df.groupby("date")["meals_served"].sum().mean())

        # Waste reduction: % of prepared meals NOT discarded
        serve_rate = round(
            (1 - summary["total_discarded"] / summary["total_prepared"]) * 100, 1
        ) if summary["total_prepared"] > 0 else None

        return avg_served, serve_rate, sdg_score
    except Exception:
        return None, None, None

_forecast_val, _serve_rate, _sdg = _landing_metrics()

# ── Page content ──────────────────────────────────────────────────────────────
st.markdown("## 🌱 FoodWise AI")
st.markdown(
    "<p style='color:#8b9cc8;font-weight:600;font-size:1.1rem;margin-top:-8px;'>"
    "AI-powered College Canteen Management · UN SDG 12</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.success(
    "✅ **App is running!** Use the sidebar to navigate between pages.\n\n"
    "This app supports **UN SDG 12 – Responsible Consumption and Production**."
)

st.info(
    "**Getting started:** Go to **🏠 Home Dashboard** in the sidebar to begin.\n\n"
    "_Note: This application uses a clearly-labelled synthetic dataset for "
    "development and testing. It is not real-world evidence._"
)

col1, col2, col3 = st.columns(3)
col1.metric(
    "🍽️ Avg Meals / Day",
    f"{_forecast_val:,}" if _forecast_val else "—",
    help="Average meals served per day across all records.",
)
col2.metric(
    "♻️ Meals Not Wasted",
    f"{_serve_rate}%" if _serve_rate else "—",
    help="(Prepared − Discarded) / Prepared × 100. Higher is better.",
)
col3.metric(
    "🌱 SDG 12 Score",
    f"{_sdg}" if _sdg else "—",
    help="100 − waste_rate. Higher is better. Based on recorded data only.",
)

# ── Show auto-seed status in sidebar ─────────────────────────────────────────
if _seed_messages:
    with st.sidebar:
        with st.expander("⚙️ Startup log", expanded=False):
            for msg in _seed_messages:
                st.caption(msg)
