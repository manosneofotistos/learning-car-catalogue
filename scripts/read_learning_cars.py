# CHECKPOINT 6: store and retrieve a place in SQLite.
"""Read persisted cars using a new database connection."""

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "learning.db"

if not DATABASE_PATH.exists():
    raise SystemExit("Run scripts/create_learning_database.py first.")

connection = sqlite3.connect(DATABASE_PATH)

# Return rows that support column names, instead of only tuple positions.
connection.row_factory = sqlite3.Row

try:
    cursor = connection.execute(
        """
        SELECT id, name, category
        FROM cars
        ORDER BY id
        """
    )

    # Fetch the result rows from the executed query.
    cars = cursor.fetchall()

    print(f"Found {len(cars)} car(s).")

    for car in cars:
        print(
            f"{car['id']} | "
            f"{car['name']} | "
            f"{car['category']}"
        )

finally:
    connection.close()