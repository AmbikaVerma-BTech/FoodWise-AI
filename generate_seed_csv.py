"""
scripts/generate_seed_csv.py
Run once to produce data/synthetic/synthetic_365.csv.
This CSV is bundled in the repo so the app can auto-seed itself on cloud
deployments where the filesystem is ephemeral.

Usage:
    python scripts/generate_seed_csv.py
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.generate_synthetic import generate_synthetic_data

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "synthetic", "synthetic_365.csv"
)


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = generate_synthetic_data(n_days=365, seed=42)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
