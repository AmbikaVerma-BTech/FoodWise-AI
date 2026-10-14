
"""
src/ui_styles.py
Shared CSS injection for FoodWise AI.
Call inject_styles() at the top of every page to apply the dark theme
custom styling — bold headings, glowing metric cards, animated buttons,
and interactive hover effects.
"""

import streamlit as st


_CSS = """
<style>
/* ── Font stack (system UI — no external requests) ───────────────────────── */
html, body, [class*="css"] {
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif !important;
}

/* ── Global background ───────────────────────────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0e1117 0%, #1a1f2e 100%);
    min-height: 100vh;
}

/* ── Main headings ───────────────────────────────────────────────────────── */
h1 {
    font-weight: 800 !important;
    font-size: 2.2rem !important;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #4f9cf9, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem !important;
}

h2 {
    font-weight: 700 !important;
    color: #e8eaf0 !important;
    border-left: 4px solid #4f9cf9;
    padding-left: 12px;
    margin-top: 1.4rem !important;
}

h3 {
    font-weight: 700 !important;
    color: #c5cae9 !important;
}

/* ── Metric cards ────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #1e2538, #252d42) !important;
    border: 1px solid #2e3a55 !important;
    border-radius: 14px !important;
    padding: 18px 22px !important;
    box-shadow: 0 4px 20px rgba(79, 156, 249, 0.08) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 28px rgba(79, 156, 249, 0.18) !important;
    border-color: #4f9cf9 !important;
}

[data-testid="metric-container"] label {
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #8b9cc8 !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-weight: 800 !important;
    font-size: 2rem !important;
    color: #4f9cf9 !important;
}

/* ── Primary buttons ─────────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f9cf9 0%, #7c5cd8 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.6rem !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 4px 15px rgba(79, 156, 249, 0.35) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    cursor: pointer !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 25px rgba(79, 156, 249, 0.55) !important;
}

.stButton > button[kind="primary"]:active {
    transform: translateY(0) scale(0.99) !important;
}

/* ── Secondary buttons ───────────────────────────────────────────────────── */
.stButton > button:not([kind="primary"]) {
    background: #1e2538 !important;
    color: #4f9cf9 !important;
    font-weight: 600 !important;
    border: 1.5px solid #4f9cf9 !important;
    border-radius: 10px !important;
    transition: background 0.15s ease !important;
}

.stButton > button:not([kind="primary"]):hover {
    background: #2a3350 !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #1a1f2e 100%) !important;
    border-right: 1px solid #2e3a55 !important;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    font-weight: 600 !important;
}

[data-testid="stSidebarNavItems"] a {
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: background 0.15s ease !important;
}

[data-testid="stSidebarNavItems"] a:hover {
    background: rgba(79, 156, 249, 0.12) !important;
}

/* ── Dataframes / tables ─────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #2e3a55 !important;
}

/* ── Input widgets ───────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div,
[data-testid="stDateInput"] > div,
[data-testid="stNumberInput"] > div {
    border-radius: 10px !important;
}

div[data-baseweb="select"] > div {
    background-color: #1e2538 !important;
    border-color: #2e3a55 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: border-color 0.2s ease !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: #4f9cf9 !important;
}

/* ── Sliders ─────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] label {
    font-weight: 700 !important;
}

[data-testid="stSlider"] [data-testid="stSlider"] {
    accent-color: #4f9cf9 !important;
}

/* ── Expanders ───────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #2e3a55 !important;
    border-radius: 12px !important;
    background: #1a1f2e !important;
}

[data-testid="stExpander"] summary {
    font-weight: 700 !important;
    color: #e8eaf0 !important;
}

/* ── Alert / info boxes ──────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* ── Form ────────────────────────────────────────────────────────────────── */
[data-testid="stForm"] {
    background: #1a1f2e !important;
    border: 1px solid #2e3a55 !important;
    border-radius: 14px !important;
    padding: 1.2rem !important;
}

/* ── Labels ──────────────────────────────────────────────────────────────── */
label[data-testid="stWidgetLabel"] p,
.stSelectbox label,
.stSlider label,
.stDateInput label,
.stNumberInput label,
.stTextInput label,
.stCheckbox label {
    font-weight: 700 !important;
    color: #c5cae9 !important;
}

/* ── Checkbox ────────────────────────────────────────────────────────────── */
.stCheckbox label span {
    font-weight: 600 !important;
}

/* ── Caption / footer text ───────────────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #5a6a8a !important;
    font-style: italic !important;
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr {
    border-color: #2e3a55 !important;
    margin: 1.2rem 0 !important;
}

/* ── Plotly chart background ─────────────────────────────────────────────── */
.js-plotly-plot .plotly .bg {
    fill: transparent !important;
}

/* ── Download button ─────────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: #1e2538 !important;
    color: #4f9cf9 !important;
    font-weight: 700 !important;
    border: 1.5px solid #4f9cf9 !important;
    border-radius: 10px !important;
    transition: background 0.15s ease, box-shadow 0.15s ease !important;
}

[data-testid="stDownloadButton"] > button:hover {
    background: #2a3350 !important;
    box-shadow: 0 4px 14px rgba(79, 156, 249, 0.3) !important;
}

/* ── Spinner ─────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] {
    color: #4f9cf9 !important;
}

/* ── Tab bar ─────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 2px solid #2e3a55 !important;
}

[data-testid="stTabs"] button[role="tab"] {
    font-weight: 700 !important;
    color: #8b9cc8 !important;
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #4f9cf9 !important;
    border-bottom: 3px solid #4f9cf9 !important;
}

/* ── Page title badge ────────────────────────────────────────────────────── */
.page-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1e2d4a, #1e2538);
    border: 1px solid #2e3a55;
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 0.78rem;
    font-weight: 700;
    color: #4f9cf9;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
</style>
"""


def inject_styles() -> None:
    """Inject FoodWise AI dark theme CSS. Call once at the top of each page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = "") -> None:
    """
    Render a styled page header with gradient title and optional subtitle.

    Parameters
    ----------
    icon     : str   Emoji icon shown before the title
    title    : str   Page title text
    subtitle : str   Optional italic caption below the title
    """
    inject_styles()   # idempotent: Streamlit deduplicates identical markdown
    st.markdown(f"## {icon} {title}")
    if subtitle:
        st.markdown(f"<p style='color:#8b9cc8;font-weight:600;margin-top:-8px;'>{subtitle}</p>",
                    unsafe_allow_html=True)
    st.markdown("---")
