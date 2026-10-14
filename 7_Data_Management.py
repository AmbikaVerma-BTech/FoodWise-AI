"""
Page 7 — Data Management
Import synthetic dataset, upload real CSV, export data, clear database.
"""

import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.database import bulk_insert_from_df, get_all_records, clear_all_records
from src.generate_synthetic import generate_synthetic_data
from src.ui_styles import page_header

st.set_page_config(page_title="Data Management", page_icon="🗄️", layout="wide")
page_header("🗄️", "Data Management", "Import, export, and manage meal records.")

REQUIRED_COLUMNS = [
    "date", "day_of_week", "meal_period", "menu_item",
    "is_special_event", "attendance_estimate", "pre_orders",
    "meals_ordered", "meals_prepared", "meals_served",
    "leftovers", "discarded", "is_synthetic",
]

# ── Load synthetic data ────────────────────────────────────────────────────────
st.subheader("1️⃣ Load Synthetic Dataset")
st.info(
    "⚠️ **Synthetic data notice:** This dataset is computer-generated with "
    "realistic statistical patterns. It is labelled `is_synthetic = 1` "
    "throughout. It is **not real-world evidence** and must never be presented as such."
)

col1, col2 = st.columns(2)
with col1:
    n_days = st.slider("📅 Number of days to generate", 180, 730, 365, 30)
with col2:
    seed = st.number_input("🔢 Random seed (for reproducibility)", value=42)

if st.button("⚡ Generate & Load Synthetic Data", type="primary", use_container_width=True):
    with st.spinner("Generating synthetic data…"):
        try:
            existing = get_all_records()
            if not existing.empty:
                st.warning(
                    "⚠️ The database already contains records. "
                    "Loading again will add duplicates. "
                    "Clear the database first (Danger Zone below) if you want a fresh import."
                )
            df_syn = generate_synthetic_data(n_days=n_days, seed=int(seed))
            bulk_insert_from_df(df_syn)
            st.success(
                f"✅ Loaded {len(df_syn)} synthetic records into the database. "
                "All rows are labelled `is_synthetic = 1`."
            )
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")

# ── Upload real CSV ────────────────────────────────────────────────────────────
st.subheader("2️⃣ Upload Real Canteen Data (CSV)")
st.markdown(
    "Your CSV must have these columns: `" + "`, `".join(REQUIRED_COLUMNS) + "`  \n"
    "Set `is_synthetic = 0` for real data."
)

uploaded = st.file_uploader("📂 Choose a CSV file", type=["csv"])
if uploaded:
    try:
        df_up = pd.read_csv(uploaded)
        missing = [c for c in REQUIRED_COLUMNS if c not in df_up.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            st.dataframe(df_up.head(), use_container_width=True)
            if st.button("📥 Import this CSV into database", type="primary", use_container_width=True):
                bulk_insert_from_df(df_up)
                st.success(f"✅ Imported {len(df_up)} records.")
    except Exception as e:
        st.error(f"Could not read file: {e}")

st.markdown("---")

# ── Export ─────────────────────────────────────────────────────────────────────
st.subheader("3️⃣ Export All Records")
try:
    df_all = get_all_records()
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download all records as CSV",
            data=csv,
            file_name="foodwise_export.csv",
            mime="text/csv",
        )
    else:
        st.info("No records to export yet.")
except Exception as e:
    st.warning(f"Export error: {e}")

st.markdown("---")

# ── Danger zone ────────────────────────────────────────────────────────────────
st.subheader("4️⃣ Danger Zone")
with st.expander("⚠️ Clear all records from database"):
    st.error("🗑️ This will permanently delete **ALL** meal records. This cannot be undone.")
    confirm = st.text_input('Type **DELETE ALL** to confirm')
    if st.button("🗑️ Clear Database", type="primary"):
        if confirm == "DELETE ALL":
            clear_all_records()
            st.success("✅ Database cleared.")
        else:
            st.warning('You must type "DELETE ALL" exactly to confirm.')

st.markdown("---")
st.caption("FoodWise AI · Synthetic data is labelled is_synthetic=1 throughout.")
