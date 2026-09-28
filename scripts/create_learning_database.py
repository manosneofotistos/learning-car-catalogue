# CHECKPOINT 6: store and retrieve a place in SQLite.
"""Create a learning database containing a cars table."""

import sqlite3
from pathlib import Path


# Resolve paths from this script's location, not the terminal's current folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "learning.db"

# SQLite can create a database file, but its parent directory must exist first.
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Open the database file, creating it if it does not already exist.
connection = sqlite3.connect(DATABASE_PATH)

try:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            variant TEXT NOT NULL,
            description TEXT NOT NULL,
            tip TEXT NOT NULL
        )
        """
    )

    # Explicitly finish any pending transaction.
    connection.commit()

    print(f"Database ready: {DATABASE_PATH}")

finally:
    # Always release the connection, even if an operation raises an exception.
    connection.close()