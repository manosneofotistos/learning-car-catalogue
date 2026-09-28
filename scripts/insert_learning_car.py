# CHECKPOINT 6: store and retrieve a place in SQLite.
"""Insert one car into the learning database."""

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "learning.db"

# Give a clear instruction if the setup script has not been run.
if not DATABASE_PATH.exists():
    raise SystemExit("Run scripts/create_learning_database.py first.")

connection = sqlite3.connect(DATABASE_PATH)

try:
    # Keep data separate from the SQL statement.
    values = (
        "Toyota Corolla",
        "Hatchback",
        "Toyota",
        "1.8 Hybrid Design",
        "A compact hybrid hatchback with supportive seats and a quiet cabin.",
        "Check the driving position.",
    )

    cursor = connection.execute(
        """
        INSERT INTO cars (
            name,
            category,
            manufacturer,
            variant,
            description,
            tip
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        values,
    )

    # Make the insertion durable before reporting success.
    connection.commit()

    # SQLite generated the ID; the cursor tells us what it was.
    print(f"Created car with ID {cursor.lastrowid}")

except sqlite3.Error:
    # Discard pending changes if a database operation fails.
    connection.rollback()
    raise

finally:
    connection.close()