"""
Page 4 — Meal Records
Add, view, and export individual meal records.

Improvements:
  • Smart defaults — today's date, meal period from current time, remembered menu item.
  • Fewer inputs — staff enter Prepared + Served; Leftovers auto-calculated, Discarded editable.
  • Friendly validation — no stack traces, clear messages with actual numbers.
  • Batch (end-of-day) entry tab — record all three meal periods in one submit.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.database import insert_record, get_all_records, delete_record
from src.features import ALL_MENU_ITEMS
from src.ui_styles import page_header

# ── Per-period menu item lists (mirrors generate_synthetic.py) ─────────────────
_PERIOD_ITEMS = {
    "Breakfast": ["Idli & Sambar", "Poha", "Bread & Omelette", "Upma", "Paratha"],
    "Lunch":     ["Rice & Curry", "Dal & Roti", "Fried Rice", "Noodles", "Pasta"],
    "Dinner":    ["Rice & Curry", "Soup", "Sandwich", "Salad Bowl", "Dal & Roti"],
}

st.set_page_config(page_title="Meal Records", page_icon="🍽️", layout="wide")
page_header("🍽️", "Meal Records", "Record what was prepared, served, and wasted for each meal.")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _default_period() -> str:
    """Return the meal period that best matches the current time."""
    hour = datetime.now().hour
    if hour < 11:
        return "Breakfast"
    elif hour < 16:
        return "Lunch"
    else:
        return "Dinner"


def _period_index(period: str) -> int:
    return ["Breakfast", "Lunch", "Dinner"].index(period)


def _menu_default(period: str) -> int:
    """Return index of the last-used menu item for this period, or 0."""
    key = f"last_menu_{period}"
    items = _PERIOD_ITEMS[period]
    last = st.session_state.get(key, items[0])
    return items.index(last) if last in items else 0


def _validate(prepared: int, served: int, discarded: int,
              leftovers: int) -> tuple[list[str], list[str]]:
    """
    Return (errors, warnings).
    errors   → block save.
    warnings → show but still allow save.
    """
    errors, warnings = [], []

    if any(v < 0 for v in [prepared, served, discarded, leftovers]):
        errors.append("❌ No quantity can be negative.")

    if served > prepared:
        errors.append(
            f"❌ Served ({served}) cannot exceed Prepared ({prepared})."
        )

    expected_lft = max(0, prepared - served)
    if leftovers != expected_lft:
        warnings.append(
            f"⚠️ Served ({served}) + Leftovers ({leftovers}) = {served + leftovers}, "
            f"but Prepared = {prepared}. "
            f"Expected Leftovers = {expected_lft}. Record saved — please double-check."
        )

    if discarded > leftovers:
        warnings.append(
            f"⚠️ Discarded ({discarded}) exceeds Leftovers ({leftovers}). "
            "That means more was thrown away than was left over. "
            "Record saved — please verify."
        )

    return errors, warnings


def _save(rec_date, meal_period, menu_item, is_special,
          attendance, pre_orders, meals_ordered,
          meals_prepared, meals_served, leftovers, discarded) -> bool:
    """Insert one record. Returns True on success."""
    try:
        insert_record(
            date=str(rec_date),
            day_of_week=rec_date.strftime("%A"),
            meal_period=meal_period,
            menu_item=menu_item,
            is_special_event=int(is_special),
            attendance_estimate=int(attendance),
            pre_orders=int(pre_orders),
            meals_ordered=int(meals_ordered),
            meals_prepared=int(meals_prepared),
            meals_served=int(meals_served),
            leftovers=int(leftovers),
            discarded=int(discarded),
            is_synthetic=0,
        )
        # Remember last menu item choice for this period
        st.session_state[f"last_menu_{meal_period}"] = menu_item
        return True
    except Exception as exc:
        st.error(f"Could not save record: {exc}")
        return False


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_single, tab_batch, tab_view = st.tabs(
    ["➕ Single Entry", "📋 End-of-Day Batch", "📊 View & Export"]
)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single Entry
# ══════════════════════════════════════════════════════════════════════════════
with tab_single:
    st.markdown("#### Add one meal record")

    default_period = _default_period()

    with st.form("single_entry_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            rec_date = st.date_input("📅 Date", value=date.today())
            meal_period = st.selectbox(
                "🍴 Meal Period",
                ["Breakfast", "Lunch", "Dinner"],
                index=_period_index(default_period),
            )
        with col2:
            # Menu items filtered to the selected period
            period_items = _PERIOD_ITEMS[meal_period]
            menu_item = st.selectbox(
                "🥘 Menu Item",
                period_items,
                index=_menu_default(meal_period),
            )
            is_special = st.checkbox("🎉 Special event?")
        with col3:
            attendance = st.number_input("👥 Attendance estimate", min_value=0, value=300)
            pre_orders = st.number_input("📝 Pre-orders", min_value=0, value=0)

        st.markdown("**📦 Quantities (portions)**")
        st.caption("Enter Prepared and Served — Leftovers is calculated automatically.")

        col_a, col_b, col_c, col_d = st.columns(4)
        meals_ordered  = col_a.number_input("Ordered",   min_value=0, value=0,
                                            help="Total orders received (optional)")
        meals_prepared = col_b.number_input("Prepared ✱", min_value=0, value=0,
                                            help="How many portions were cooked")
        meals_served   = col_c.number_input("Served ✱",   min_value=0, value=0,
                                            help="How many portions were given out")

        # Auto-calculate leftovers; show as read-only hint
        auto_leftovers = max(0, meals_prepared - meals_served)
        col_d.metric("Leftovers (auto)", auto_leftovers,
                     help="Prepared − Served, calculated automatically")

        discarded = st.number_input(
            "🗑️ Discarded",
            min_value=0,
            value=auto_leftovers,
            help="Defaults to Leftovers. Edit down if some leftovers were stored safely.",
        )

        submitted = st.form_submit_button(
            "💾 Save Record", type="primary", use_container_width=True
        )

    if submitted:
        errors, warnings = _validate(meals_prepared, meals_served,
                                     discarded, auto_leftovers)
        if errors:
            for e in errors:
                st.error(e)
        else:
            for w in warnings:
                st.warning(w)
            if _save(rec_date, meal_period, menu_item, is_special,
                     attendance, pre_orders, meals_ordered,
                     meals_prepared, meals_served, auto_leftovers, discarded):
                st.success(
                    f"✅ Saved: **{menu_item}** · {meal_period} · {rec_date} · "
                    f"{meals_prepared} prepared, {meals_served} served, "
                    f"{auto_leftovers} left over, {discarded} discarded."
                )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — End-of-Day Batch Entry
# ══════════════════════════════════════════════════════════════════════════════
with tab_batch:
    st.markdown("#### Record all three meal periods for one day in a single submit")
    st.info(
        "Fill in Prepared and Served for each period. "
        "Leftovers are auto-calculated. Discarded defaults to Leftovers — edit if needed."
    )

    with st.form("batch_entry_form"):
        batch_date   = st.date_input("📅 Date", value=date.today(), key="batch_date")
        batch_special = st.checkbox("🎉 Special event for the whole day?", key="batch_special")
        batch_attend  = st.number_input("👥 Attendance estimate (whole day)",
                                        min_value=0, value=300, key="batch_attend")

        st.markdown("---")

        batch_rows = {}
        for period in ["Breakfast", "Lunch", "Dinner"]:
            st.markdown(f"**{period}**")
            items = _PERIOD_ITEMS[period]
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
            with c1:
                mi = st.selectbox(
                    "Menu Item", items,
                    index=_menu_default(period),
                    key=f"batch_item_{period}",
                )
            with c2:
                prep = st.number_input("Prepared", min_value=0, value=0,
                                       key=f"batch_prep_{period}")
            with c3:
                serv = st.number_input("Served",   min_value=0, value=0,
                                       key=f"batch_serv_{period}")
            lft = max(0, prep - serv)
            with c4:
                st.metric("Leftovers", lft)
            with c5:
                disc = st.number_input("Discarded", min_value=0, value=lft,
                                       key=f"batch_disc_{period}")
            batch_rows[period] = dict(
                menu_item=mi, meals_prepared=prep,
                meals_served=serv, leftovers=lft, discarded=disc,
            )

        batch_submitted = st.form_submit_button(
            "💾 Save All Three Periods", type="primary", use_container_width=True
        )

    if batch_submitted:
        all_errors = []
        all_warnings = []
        for period, row in batch_rows.items():
            errs, warns = _validate(
                row["meals_prepared"], row["meals_served"],
                row["discarded"], row["leftovers"],
            )
            for e in errs:
                all_errors.append(f"**{period}:** {e}")
            for w in warns:
                all_warnings.append(f"**{period}:** {w}")

        if all_errors:
            for e in all_errors:
                st.error(e)
        else:
            for w in all_warnings:
                st.warning(w)
            saved_count = 0
            for period, row in batch_rows.items():
                ok = _save(
                    batch_date, period, row["menu_item"],
                    batch_special, batch_attend,
                    pre_orders=0, meals_ordered=0,
                    meals_prepared=row["meals_prepared"],
                    meals_served=row["meals_served"],
                    leftovers=row["leftovers"],
                    discarded=row["discarded"],
                )
                if ok:
                    saved_count += 1
            if saved_count == 3:
                st.success(f"✅ All 3 meal periods saved for {batch_date}.")
            elif saved_count > 0:
                st.warning(f"⚠️ {saved_count}/3 periods saved — check errors above.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — View & Export
# ══════════════════════════════════════════════════════════════════════════════
with tab_view:
    st.markdown("#### All Meal Records")
    try:
        df = get_all_records()
        if df.empty:
            st.info("No records yet. Use the Single Entry or Batch tabs to add records.")
        else:
            # Filters
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                periods = ["All"] + sorted(df["meal_period"].unique().tolist())
                filter_period = st.selectbox("Filter by Meal Period", periods, key="vw_period")
            with fc2:
                items = ["All"] + sorted(df["menu_item"].unique().tolist())
                filter_item = st.selectbox("Filter by Menu Item", items, key="vw_item")
            with fc3:
                filter_synth = st.selectbox(
                    "Data type", ["All", "Real only", "Synthetic only"], key="vw_synth"
                )

            df_view = df.copy()
            if filter_period != "All":
                df_view = df_view[df_view["meal_period"] == filter_period]
            if filter_item != "All":
                df_view = df_view[df_view["menu_item"] == filter_item]
            if filter_synth == "Real only":
                df_view = df_view[df_view["is_synthetic"] == 0]
            elif filter_synth == "Synthetic only":
                df_view = df_view[df_view["is_synthetic"] == 1]

            st.caption(f"Showing {len(df_view):,} of {len(df):,} records")

            display_cols = ["date", "meal_period", "menu_item",
                            "meals_prepared", "meals_served", "leftovers",
                            "discarded", "is_synthetic"]
            st.dataframe(df_view[display_cols].sort_values("date", ascending=False),
                         use_container_width=True, hide_index=True)

            csv = df_view.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Export filtered records as CSV",
                data=csv,
                file_name="foodwise_meal_records.csv",
                mime="text/csv",
            )
    except Exception as exc:
        st.warning(f"Could not load records: {exc}")

st.markdown("---")
st.caption(
    "FoodWise AI · Leftovers = Prepared − Served · Discarded ≤ Leftovers · "
    "Real records are labelled is_synthetic = 0"
)
