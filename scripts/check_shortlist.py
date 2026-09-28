#Checkpoint 12: introduce the shared shortlist as a related table.
"""Demonstrate shortlist relationships using one temporary car."""

import sqlite3

from app import db


def main():
    # Ensure the tables exist before running the exercise.
    db.initialize()

    # Use our own record so the exercise leaves existing cars untouched.
    car = db.create_car(
        {
            "name": "Shortlist Practice Coupe",
            "category": "Coupe",
            "manufacturer": "Toyota",
            "variant": "Relationship Demo Edition",
            "description": (
                "A temporary example for learning how cars "
                "and shortlist entries relate to one another."
            ),
            "tip": "This example is removed when the exercise finishes.",
        }
    )
    car_id = car["id"]

    try:
        # 1. Save the car by inserting only its ID.
        with db.connect() as connection:
            connection.execute(
                "INSERT INTO shortlist (car_id) VALUES (?)",
                (car_id,),
            )

        print("1. Saved the temporary car.")

        # 2. Open a new connection and combine the related rows.
        with db.connect() as connection:
            saved_car = connection.execute(
                """
                SELECT p.id, p.name, p.category
                FROM shortlist AS s
                JOIN cars AS p ON p.id = s.car_id
                WHERE s.car_id = ?
                """,
                (car_id,),
            ).fetchone()

        assert saved_car is not None
        print(f"2. JOIN found: {saved_car['name']}")

        # 3. The primary key must reject a duplicate shortlist entry.
        # Catch the exception outside the with block so it rolls back first.
        try:
            with db.connect() as connection:
                connection.execute(
                    "INSERT INTO shortlist (car_id) VALUES (?)",
                    (car_id,),
                )
        except sqlite3.IntegrityError:
            print("3. Duplicate save rejected.")
        else:
            raise AssertionError("The database accepted a duplicate save.")

        # 4. Delete the car. We do not explicitly delete its shortlist row.
        deleted = db.delete_car(car_id)
        assert deleted

        with db.connect() as connection:
            remaining = connection.execute(
                "SELECT car_id FROM shortlist WHERE car_id = ?",
                (car_id,),
            ).fetchone()

        assert remaining is None
        print("4. Deleting the car also removed its shortlist entry.")

        # 5. The deleted ID no longer references an existing car.
        try:
            with db.connect() as connection:
                connection.execute(
                    "INSERT INTO shortlist (car_id) VALUES (?)",
                    (car_id,),
                )
        except sqlite3.IntegrityError:
            print("5. Saving a missing car rejected.")
        else:
            raise AssertionError("The database accepted an orphan entry.")

    finally:
        # Clean up our record even if an earlier check fails.
        # If already deleted, this simply returns False.
        db.delete_car(car_id)

    print("All shortlist relationship checks passed.")


if __name__ == "__main__":
    main()