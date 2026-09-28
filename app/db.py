# # CHECKPOINT 7 — Create the application database and seed (seed.json) it. 
"""Manage SQLite connections and initialize the application database."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


APP_DIRECTORY = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIRECTORY.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "catalogue.db"

# CHECKPOINT 13 — Read car content together with shortlist membership.
# LEFT JOIN keeps unsaved cars; the response model converts membership to a boolean.
CAR_SELECT = """
    SELECT
        p.id,
        p.name,
        p.category,
        p.manufacturer,
        p.variant,
        p.description,
        p.tip,
        (s.car_id IS NOT NULL) AS shortlisted
    FROM cars AS p
    LEFT JOIN shortlist AS s ON s.car_id = p.id
"""

@contextmanager
def connect():
    """Provide a connection and handle commit, rollback, and cleanup."""
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row

    # SQLite requires foreign-key enforcement on each connection.
    # This will matter when we introduce the related shortlist table. - CHECKPOINT 12
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        # The connection's context manager commits on success
        # and rolls back pending changes if an exception occurs.
        with connection:
            yield connection
    finally:
        # The transaction context does not close the connection for us.
        connection.close()

def initialize():
    """Create missing tables and insert sample cars only once."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    schema = (APP_DIRECTORY / "schema.sql").read_text(encoding="utf-8")

    with connect() as connection:
        # This schema is a trusted local file, not user-supplied SQL.
        connection.executescript(schema)

        # Keep the seed check, inserts, and marker in one transaction.
        # Taking the write lock now prevents simultaneous initializers
        # from both deciding that seeding is required.
        connection.execute("BEGIN IMMEDIATE")

        seeded = connection.execute(
            "SELECT value FROM app_metadata WHERE key = ?",
            ("seeded",),
        ).fetchone()

        # The marker survives even when users deliberately delete every car.
        if seeded is not None:
            return

        seed_text = (APP_DIRECTORY / "seed.json").read_text(
            encoding="utf-8"
        )
        cars = json.loads(seed_text)

        for car in cars:
            connection.execute(
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
                (
                    car["name"],
                    car["category"],
                    car["manufacturer"],
                    car["variant"],
                    car["description"],
                    car["tip"],
                ),
            )

        # Write the marker only after every sample insert succeeds.
        connection.execute(
            "INSERT INTO app_metadata (key, value) VALUES (?, ?)",
            ("seeded", "1"),
        )

#Checkpoint 8: make the API read from SQLite.
def list_cars(q: str = "", category: str | None = None):
    """Return cars matching the optional text and category filters."""
    # sql = """
    #     SELECT id, name, category, manufacturer, variant, description, tip
    #     FROM cars
    # """
    sql = CAR_SELECT # CHECKPOINT 13

    # Build SQL from fixed clauses. User values go in a separate parameter list.
    conditions = []
    parameters = []

    if category is not None:
        conditions.append("category = ?")
        parameters.append(category)

    search_text = q.strip()

    if search_text:
        # || joins strings in SQLite.
        # instr(text, search) returns 0 when the search text is absent.
        # lower() makes this comparison case-insensitive for ASCII letters.
        conditions.append(
            """
            instr(
                lower(name || ' ' || manufacturer || ' ' || description),
                lower(?)
            ) > 0
            """
        )
        parameters.append(search_text)

    if conditions:
        # Both filters must match when both were supplied.
        sql += " WHERE " + " AND ".join(conditions)

    # Database rows have no guaranteed order without ORDER BY.
    sql += " ORDER BY id"

    with connect() as connection:
        rows = connection.execute(sql, parameters).fetchall()

        # Convert SQLite Row objects into ordinary dictionaries for the API.
        return [dict(row) for row in rows]

#Checkpoint 8: make the API read from SQLite.
def get_car(car_id: int):
    """Return a car dictionary, or None if the ID does not exist."""
    with connect() as connection:
        # row = connection.execute(
        #     """
        #     SELECT id, name, category, manufacturer, variant, description, tip
        #     FROM cars
        #     WHERE id = ?
        #     """,
        #     (car_id,),
        # ).fetchone()
        
        # CHECKPOINT 13
        row = connection.execute(
            CAR_SELECT + " WHERE p.id = ?",
            (car_id,),
        ).fetchone()

        if row is None:
            return None

        return dict(row)

# CHECKPOINT 9 — Write changes to the application database. Create, edit, and delete cars in SQLite.
def create_car(data: dict):
    """Insert a car and return its stored content."""
    with connect() as connection:
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
            (
                data["name"],
                data["category"],
                data["manufacturer"],
                data["variant"],
                data["description"],
                data["tip"],
            ),
        )

        # SQLite generates the ID. Read the new row using this same connection.
        # row = connection.execute(
        #     """
        #     SELECT id, name, category, manufacturer, variant, description, tip
        #     FROM cars
        #     WHERE id = ?
        #     """,
        #     (cursor.lastrowid,),
        # ).fetchone()

        # CHECKPOINT 13
        row = connection.execute(
            CAR_SELECT + " WHERE p.id = ?",
            (cursor.lastrowid,),
        ).fetchone()

        return dict(row)

# CHECKPOINT 9 — Write changes to the application database.
def update_car(car_id: int, data: dict):
    """Replace a car's editable fields, or return None if it is missing."""
    with connect() as connection:
        cursor = connection.execute(
            """
            UPDATE cars
            SET name = ?,
                category = ?,
                manufacturer = ?,
                variant = ?,
                description = ?,
                tip = ?
            WHERE id = ?
            """,
            (
                data["name"],
                data["category"],
                data["manufacturer"],
                data["variant"],
                data["description"],
                data["tip"],
                car_id,
            ),
        )

        # No matching row means this ID does not exist.
        if cursor.rowcount == 0:
            return None

        # Return the updated record while still inside the same transaction.
        # row = connection.execute(
        #     """
        #     SELECT id, name, category, manufacturer, variant, description, tip
        #     FROM cars
        #     WHERE id = ?
        #     """,
        #     (car_id,),
        # ).fetchone()

        # CHECKPOINT 13
        row = connection.execute(
            CAR_SELECT + " WHERE p.id = ?",
            (car_id,),
        ).fetchone()

        return dict(row)

def delete_car(car_id: int):
    """Return True if a car was deleted, or False if it was missing."""
    with connect() as connection:
        cursor = connection.execute(
            "DELETE FROM cars WHERE id = ?",
            (car_id,),
        )

        # A primary-key lookup can match at most one row.
        return cursor.rowcount > 0

#CHECKPOINT 13
def list_shortlist():
    """Return only cars that belong to the shared shortlist."""
    with connect() as connection:
        rows = connection.execute(
            CAR_SELECT
            + " WHERE s.car_id IS NOT NULL ORDER BY p.id"
        ).fetchall()

        return [dict(row) for row in rows]

#CHECKPOINT 13
def set_shortlisted(car_id: int, shortlisted: bool):
    """Set membership and return the car, or None if it is missing."""
    with connect() as connection:
        # Keep the existence check and membership change in one write transaction.
        # Another writer cannot delete the car between these operations.
        connection.execute("BEGIN IMMEDIATE")

        exists = connection.execute(
            "SELECT 1 FROM cars WHERE id = ?",
            (car_id,),
        ).fetchone()

        if exists is None:
            return None

        if shortlisted:
            # Saving an already saved car is a successful no-op.
            connection.execute(
                """
                INSERT INTO shortlist (car_id)
                VALUES (?)
                ON CONFLICT(car_id) DO NOTHING
                """,
                (car_id,),
            )
        else:
            # Deleting an absent membership is also a successful no-op.
            connection.execute(
                "DELETE FROM shortlist WHERE car_id = ?",
                (car_id,),
            )

        # Read the resulting state before committing this transaction.
        row = connection.execute(
            CAR_SELECT + " WHERE p.id = ?",
            (car_id,),
        ).fetchone()

        return dict(row)
    
#CHECKPOINT 7
# Run initialization when this module is executed directly.
# Importing it from another module will not run this block.
if __name__ == "__main__":
    initialize()
    print(f"Database initialized: {DATABASE_PATH}")