# # CHECKPOINT 7 — Create the application database and seed (seed.json) it. 
"""Inspect application data without changing it."""

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "catalogue.db"

if not DATABASE_PATH.exists():
    raise SystemExit("Run python -m app.db first.")

connection = sqlite3.connect(DATABASE_PATH)
connection.row_factory = sqlite3.Row

try:
    cars = connection.execute(
        "SELECT id, name FROM cars ORDER BY id"
    ).fetchall()

    print(f"Cars: {len(cars)}")

    for car in cars:
        print(f"{car['id']} | {car['name']}")

    marker = connection.execute(
        "SELECT value FROM app_metadata WHERE key = ?",
        ("seeded",),
    ).fetchone()

    if marker is None:
        print("Seed marker: absent")
    else:
        print(f"Seed marker: {marker['value']}")

finally:
    connection.close()