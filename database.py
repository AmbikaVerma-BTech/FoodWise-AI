"""
src/database.py
All SQLite read/write operations for FoodWise AI.
Database file: foodwise.db (created automatically on first run).
"""

import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "foodwise.db")


def _get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    """Create the meal_records table if it does not already exist."""
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meal_records (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            date             TEXT    NOT NULL,
            day_of_week      TEXT    NOT NULL,
            meal_period      TEXT    NOT NULL,
            menu_item        TEXT    NOT NULL,
            is_special_event INTEGER NOT NULL DEFAULT 0,
            attendance_estimate INTEGER NOT NULL DEFAULT 0,
            pre_orders       INTEGER NOT NULL DEFAULT 0,
            meals_ordered    INTEGER NOT NULL DEFAULT 0,
            meals_prepared   INTEGER NOT NULL,
            meals_served     INTEGER NOT NULL,
            leftovers        INTEGER NOT NULL,
            discarded        INTEGER NOT NULL,
            is_synthetic     INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


# Initialise the database when this module is imported.
init_db()


def insert_record(**kwargs):
    """Insert a single meal record. kwargs must match meal_records columns."""
    conn = _get_connection()
    conn.execute(
        """
        INSERT INTO meal_records
            (date, day_of_week, meal_period, menu_item,
             is_special_event, attendance_estimate, pre_orders,
             meals_ordered, meals_prepared, meals_served,
             leftovers, discarded, is_synthetic)
        VALUES
            (:date, :day_of_week, :meal_period, :menu_item,
             :is_special_event, :attendance_estimate, :pre_orders,
             :meals_ordered, :meals_prepared, :meals_served,
             :leftovers, :discarded, :is_synthetic)
        """,
        kwargs,
    )
    conn.commit()
    conn.close()


def bulk_insert_from_df(df: pd.DataFrame):
    """Insert all rows of a DataFrame into meal_records."""
    conn = _get_connection()
    df.to_sql("meal_records", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()


def get_all_records() -> pd.DataFrame:
    """Return all meal records as a DataFrame."""
    conn = _get_connection()
    df = pd.read_sql("SELECT * FROM meal_records ORDER BY date", conn)
    conn.close()
    return df


def get_recent_records(limit: int = 10) -> pd.DataFrame:
    """Return the most recent `limit` meal records."""
    conn = _get_connection()
    df = pd.read_sql(
        "SELECT * FROM meal_records ORDER BY date DESC LIMIT ?", conn,
        params=(limit,)
    )
    conn.close()
    return df


def delete_record(record_id: int):
    """Delete a single record by its ID."""
    conn = _get_connection()
    conn.execute("DELETE FROM meal_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def clear_all_records():
    """Delete ALL records from meal_records. Irreversible."""
    conn = _get_connection()
    conn.execute("DELETE FROM meal_records")
    conn.commit()
    conn.close()
