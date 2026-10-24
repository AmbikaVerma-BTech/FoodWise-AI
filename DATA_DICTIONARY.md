# FoodWise AI — Data Dictionary

Every column in the `meal_records` database table and the synthetic CSV file.

---

## Table: `meal_records`

| Column | Type | Description | Example |
|---|---|---|---|
| `id` | INTEGER | Auto-incrementing primary key (database only). | 1 |
| `date` | TEXT | Calendar date of the meal. Format: YYYY-MM-DD. | 2023-06-15 |
| `day_of_week` | TEXT | Full name of the day, derived from `date`. | Thursday |
| `meal_period` | TEXT | One of: `Breakfast`, `Lunch`, `Dinner`. | Lunch |
| `menu_item` | TEXT | Name of the dish offered for this meal. | Rice & Curry |
| `is_special_event` | INTEGER | 1 if a special event occurred (exam, sports day, festival, holiday); 0 otherwise. | 0 |
| `attendance_estimate` | INTEGER | Expected number of students present on that day. | 350 |
| `pre_orders` | INTEGER | Number of portions ordered in advance before the meal period. | 40 |
| `meals_ordered` | INTEGER | Total number of portions ordered during the meal period. | 210 |
| `meals_prepared` | INTEGER | **Number of portions actually cooked.** This is the ML target variable. | 230 |
| `meals_served` | INTEGER | Number of portions actually given to students. Always ≤ `meals_prepared`. | 205 |
| `leftovers` | INTEGER | Portions prepared but not served. Always = `meals_prepared` − `meals_served`. | 25 |
| `discarded` | INTEGER | Portions from leftovers that were thrown away (food waste). Always ≤ `leftovers`. | 10 |
| `is_synthetic` | INTEGER | **Transparency flag.** Always 1 for computer-generated rows. Always 0 for real recorded rows. | 1 |

---

## Important distinctions

```
meals_ordered     → what customers asked for
      ↓
meals_prepared    → what was actually cooked  ← ML TARGET
      ↓
meals_served      → what was actually given out  (≤ prepared)
      ↓
leftovers         → prepared − served  (may be stored safely)
      ↓
discarded         → portion of leftovers thrown away  (≤ leftovers)
```

---

## Meal periods

| Period | Typical time | Typical base demand |
|---|---|---|
| Breakfast | 07:30 – 09:30 | ~120 portions |
| Lunch | 12:00 – 14:00 | ~250 portions |
| Dinner | 18:00 – 20:00 | ~180 portions |

*(Synthetic data defaults — adjust for your canteen.)*

---

## Menu items (synthetic dataset)

**Breakfast:** Idli & Sambar, Poha, Bread & Omelette, Upma, Paratha

**Lunch:** Rice & Curry, Dal & Roti, Fried Rice, Noodles, Pasta

**Dinner:** Rice & Curry, Soup, Sandwich, Salad Bowl, Dal & Roti

---

## Feature columns used by ML models

All feature engineering is implemented in `src/features.py`.
`FEATURE_COLUMNS` defines the exact ordered list used by every model.

### Temporal features

| Feature | How it is built | Why |
|---|---|---|
| `dow_sin` | sin(2π × day_of_week / 7) | Cyclical encoding — Sunday wraps around to Monday |
| `dow_cos` | cos(2π × day_of_week / 7) | Paired with dow_sin for full cyclical representation |

### Demand signal features

| Feature | How it is built | Why |
|---|---|---|
| `is_special_event` | Copied directly (0 or 1) | Demand spikes on special days |
| `attendance_estimate` | Copied directly (integer) | More students → more demand |
| `pre_orders` | Copied directly (integer) | Known advance demand signal; set to 0 at forecast time |

### Meal period one-hot encoding

| Feature | Value is 1 when… |
|---|---|
| `is_breakfast` | meal_period == "Breakfast" |
| `is_lunch` | meal_period == "Lunch" |
| `is_dinner` | meal_period == "Dinner" |

### Menu item one-hot encoding

Each menu item across all meal periods is encoded as a binary column.
Column names are derived as: `item_` + item name with spaces→`_` and `&`→`and`.

| Feature column | Menu item |
|---|---|
| `item_Idli_and_Sambar` | Idli & Sambar *(Breakfast)* |
| `item_Poha` | Poha *(Breakfast)* |
| `item_Bread_and_Omelette` | Bread & Omelette *(Breakfast)* |
| `item_Upma` | Upma *(Breakfast)* |
| `item_Paratha` | Paratha *(Breakfast)* |
| `item_Rice_and_Curry` | Rice & Curry *(Lunch / Dinner)* |
| `item_Dal_and_Roti` | Dal & Roti *(Lunch / Dinner)* |
| `item_Fried_Rice` | Fried Rice *(Lunch)* |
| `item_Noodles` | Noodles *(Lunch)* |
| `item_Pasta` | Pasta *(Lunch)* |
| `item_Soup` | Soup *(Dinner)* |
| `item_Sandwich` | Sandwich *(Dinner)* |
| `item_Salad_Bowl` | Salad Bowl *(Dinner)* |

> **Total feature count:** 8 base features + 13 menu-item features = **21 features**

---

## Sustainability metric assumptions

All sustainability metrics are calculated from recorded data using
the assumptions below. Every assumption is user-adjustable on the
Settings & Impact page.

| Assumption | Default value | Source / Note |
|---|---|---|
| `kg_per_portion` | 0.35 kg | Typical mixed canteen meal weight estimate |
| `co2_per_kg` | 2.5 kg CO₂e | IPCC default for mixed food waste |
| `cost_per_portion` | 50 INR | User-defined; no real cost baseline applied |

**No savings are claimed without a defensible real-world baseline.**

---

*FoodWise AI · Synthetic data is labelled is_synthetic=1 throughout.*
