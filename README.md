# FoodWise AI 🌱

> AI-powered college canteen management app — forecasts meal demand, tracks food waste,
> and measures sustainability impact.
>
> **Supports UN SDG 12: Responsible Consumption and Production.**

---

## ⚠️ Synthetic Data Notice

This app ships with a computer-generated synthetic dataset
(labelled `is_synthetic = 1` throughout).
**It is not real-world evidence** and must never be presented as such.
It is provided so the app runs and the models train from day one.
Replace it with your own canteen data via the Data Management page.

---

## What the app does

| Page | What you can do |
|---|---|
| 🏠 Home Dashboard | See a live summary of records, waste %, and SDG 12 score |
| 📈 Demand Forecast | Get a model-based portions forecast for any date and menu item |
| 📋 Preparation Planner | Get a suggested preparation quantity with risk flags and buffer |
| 🍽️ Meal Records | Add, view, and export meal records |
| ♻️ Waste Analytics | See waste trends broken down by meal period and menu item |
| 🤖 Model Performance | Train models and compare MAE, RMSE, WAPE scores |
| 🗄️ Data Management | Load synthetic data, upload real CSV, clear database |
| 🌍 Settings & Impact | Adjust assumptions, see CO₂ and financial waste estimates |

---

## Requirements

- Python **3.9 or later** (tested on 3.9 – 3.12)
- All packages listed in `requirements.txt`

---

## Step-by-step setup (Windows)

### 1 — Open a terminal in the project folder

```
cd path\to\foodwise-ai
```

### 2 — Create a virtual environment

```
python -m venv venv
```

### 3 — Activate the virtual environment

```
venv\Scripts\activate
```

You should see `(venv)` at the start of your prompt.

### 4 — Install all packages

```
pip install -r requirements.txt
```

This may take a few minutes. You only need to do it once.

### 5 — (Optional) Install the project as an editable package

```
pip install -e .
```

This makes `src.*` importable without any `sys.path` manipulation.
Not required — the app works without this step.

### 6 — Run the app

```
streamlit run app.py
```

The app opens automatically in your browser at `http://localhost:8501`.

### 7 — First time: the app auto-seeds itself

On first run the app automatically loads 365 days of synthetic data and
trains a model — **you don't need to click anything**.
All synthetic rows are labelled `is_synthetic = 1`.

---

## Running tests

```
pytest tests/ -v
```

---

## Project structure

```
foodwise-ai/
├── app.py                  Entry point — also auto-seeds DB + model on first run
├── pages/                  One Streamlit page per file
├── src/                    Python logic modules
│   ├── database.py         SQLite helpers
│   ├── generate_synthetic.py  Synthetic data generator
│   ├── features.py         ML feature engineering (21 features)
│   ├── models.py           Train, evaluate, save models
│   ├── forecast.py         Generate forecasts
│   ├── waste.py            Waste calculations
│   └── impact.py           Sustainability metrics
├── data/
│   ├── synthetic/          Pre-generated synthetic CSV (auto-loaded on first run)
│   └── real/               Place your real canteen CSV here
├── models/                 Saved model files (auto-created on first train)
├── tests/                  pytest unit tests
├── .streamlit/config.toml  Streamlit theme + server settings
├── pyproject.toml          Package metadata (enables pip install -e .)
├── requirements.txt
├── DATA_DICTIONARY.md
└── README.md
```

---

## Deployment (Streamlit Community Cloud)

1. Push this repository to GitHub (public or private).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo → set **Main file path** to `foodwise-ai/app.py`
   (or `app.py` if the repo root is `foodwise-ai/`).
4. Click **Deploy**. Your app gets a public URL instantly.

> **Cloud note:** Streamlit Community Cloud has an ephemeral filesystem.
> The SQLite database resets on every restart.
> The app auto-reseeds from the bundled CSV on each cold start, so it always
> works — but any manually-added real records will not survive a restart.
> Export your data as CSV before closing the session.
---

## Honest limitations

- The synthetic dataset (~1 095 rows for 365 days × 3 meal periods) is small.
  Model scores demonstrate that the pipeline works but are **not real-world
  performance evidence**.
- SQLite data is **not persistent on Streamlit Community Cloud**. Export a CSV
  before every restart when using cloud deployment.
- No savings (food or money) are claimed without a real baseline and
  recorded evidence.
- The uncertainty range is a heuristic (±1 residual std), not a calibrated
  probability interval.

---

## Technology stack

| Purpose | Library |
|---|---|
| Web UI | Streamlit 1.35 |
| Charts | Plotly 5.22 |
| Data | Pandas 2.2, NumPy 1.26 |
| ML models | scikit-learn 1.5 |
| Model save/load | joblib 1.4 |
| Database | SQLite (built-in) |
| Tests | pytest 8.2 |

---

## ML model details

Four models are trained and compared on a **chronological 80/20 split**
(no shuffling — prevents data leakage):

| Model | Notes |
|---|---|
| Naive Baseline | Predicts training-set mean for every row |
| Linear Regression | Fast, interpretable |
| Random Forest | Ensemble — handles non-linearity |
| Gradient Boosting | Usually best performer |

The model with lowest MAE on the test set is saved as `best_model.joblib`.

**Features (21 total):** day-of-week (sin/cos), is_special_event,
attendance_estimate, pre_orders, meal period (3 one-hot), menu item (13 one-hot).

---

## SDG 12 alignment

This app supports **SDG Target 12.3**:
> "By 2030, halve per capita global food waste at the retail and consumer
> levels and reduce food losses along production and supply chains."
>
> — United Nations Sustainable Development Goals

---

*Built as an AI/ML internship project using IBM Bob.*
