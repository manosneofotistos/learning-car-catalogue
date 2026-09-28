#CHECKPOINT 14 automate the backend checks using temporary databases.
"""Check HTTP behavior against real, isolated SQLite databases."""


import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


def test_list_filters_and_missing_car(client):
    # Request parameters are encoded by the client.
    response = client.get(
        "/api/cars",
        params={"q": "toyota", "category": "Coupe"},
    )

    assert response.status_code == 200
    cars = response.json()
    assert [car["name"] for car in cars] == ["Toyota GR86"]
    assert cars[0]["shortlisted"] is False

    response = client.get("/api/cars", params={"q": "spaceship"})
    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/api/cars/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "This car does not exist."

def test_invalid_input_does_not_create_a_car(client, example_car):
    before = client.get("/api/cars").json()

    # Start from valid content and make one field invalid.
    invalid_car = {**example_car, "name": " "}
    response = client.post("/api/cars", json=invalid_car)

    assert response.status_code == 422
    assert client.get("/api/cars").json() == before

    # Query parameters have validation rules too.
    response = client.get("/api/cars", params={"category": "Other"})
    assert response.status_code == 422

    response = client.get("/api/cars", params={"q": "x" * 101})
    assert response.status_code == 422

    # A string is not accepted in place of a JSON boolean.
    car_id = before[0]["id"]
    response = client.put(
        f"/api/cars/{car_id}/shortlist",
        json={"shortlisted": "true"},
    )

    assert response.status_code == 422
    assert client.get("/api/shortlist").json() == []

def test_car_lifecycle_and_shortlist(client, example_car):
    # Create.
    response = client.post("/api/cars", json=example_car)
    assert response.status_code == 201

    created = response.json()
    assert created["name"] == example_car["name"]
    assert created["shortlisted"] is False

    car_id = created["id"]
    path = f"/api/cars/{car_id}"

    # Retrieve independently.
    assert client.get(path).json() == created

    # Replace the editable content.
    updated_input = {**example_car, "name": "Updated Test Coupe"}
    response = client.put(path, json=updated_input)

    assert response.status_code == 200
    assert response.json()["name"] == updated_input["name"]
    assert response.json()["id"] == car_id
    assert client.get(path).json()["name"] == updated_input["name"]

    # Repeating a save must not duplicate or reverse membership.
    for _ in range(2):
        response = client.put(
            path + "/shortlist",
            json={"shortlisted": True},
        )
        assert response.status_code == 200
        assert response.json()["shortlisted"] is True

    saved = client.get("/api/shortlist").json()
    assert [car["id"] for car in saved] == [car_id]

    # Repeating removal must also succeed.
    for _ in range(2):
        response = client.put(
            path + "/shortlist",
            json={"shortlisted": False},
        )
        assert response.status_code == 200
        assert response.json()["shortlisted"] is False

    assert client.get("/api/shortlist").json() == []
    assert client.get(path).status_code == 200

    # Save again, then delete the parent car to exercise the cascade.
    response = client.put(path + "/shortlist", json={"shortlisted": True})
    assert response.status_code == 200

    response = client.delete(path)
    assert response.status_code == 204
    assert response.content == b""

    assert client.get("/api/shortlist").json() == []

    # Inspect the underlying table too: no orphan membership should remain.
    with db.connect() as connection:
        remaining = connection.execute(
            "SELECT car_id FROM shortlist WHERE car_id = ?",
            (car_id,),
        ).fetchone()

    assert remaining is None

    # Missing records have consistent behavior across routes.
    assert client.get(path).status_code == 404
    assert client.delete(path).status_code == 404
    assert client.put(path, json=updated_input).status_code == 404

    response = client.put(
        path + "/shortlist",
        json={"shortlisted": True},
    )
    assert response.status_code == 404

def test_restart_preserves_data_without_reseeding(database, example_car):
    # This test manages startup/shutdown itself instead of using client.
    with TestClient(app) as first:
        initial_cars = first.get("/api/cars").json()
        initial_count = len(initial_cars)
        deleted_seed_id = initial_cars[0]["id"]

        response = first.post("/api/cars", json=example_car)
        assert response.status_code == 201
        created_id = response.json()["id"]

        response = first.put(
            f"/api/cars/{created_id}/shortlist",
            json={"shortlisted": True},
        )
        assert response.status_code == 200

        response = first.delete(f"/api/cars/{deleted_seed_id}")
        assert response.status_code == 204

    # Startup runs again, using the same temporary database file.
    with TestClient(app) as restarted:
        cars = restarted.get("/api/cars").json()

        # One creation and one deletion leave the total unchanged.
        assert len(cars) == initial_count
        assert restarted.get(
            f"/api/cars/{deleted_seed_id}"
        ).status_code == 404

        persisted = restarted.get(f"/api/cars/{created_id}").json()
        assert persisted["name"] == example_car["name"]
        assert persisted["shortlisted"] is True

        # An intentionally empty catalogue must also remain empty after startup.
        for car in cars:
            response = restarted.delete(f"/api/cars/{car['id']}")
            assert response.status_code == 204

    with TestClient(app) as empty_restart:
        assert empty_restart.get("/api/cars").json() == []
        assert empty_restart.get("/api/shortlist").json() == []

def test_database_rejects_orphans_and_duplicate_membership(database):
    db.initialize()

    cars = db.list_cars()
    existing_id = cars[0]["id"]
    missing_id = max(car["id"] for car in cars) + 1

    # Bypass the API deliberately: the foreign key must still protect the data.
    with pytest.raises(sqlite3.IntegrityError):
        with db.connect() as connection:
            connection.execute(
                "INSERT INTO shortlist (car_id) VALUES (?)",
                (missing_id,),
            )

    # Save once successfully.
    with db.connect() as connection:
        connection.execute(
            "INSERT INTO shortlist (car_id) VALUES (?)",
            (existing_id,),
        )

    # A raw duplicate INSERT must fail at the database boundary.
    with pytest.raises(sqlite3.IntegrityError):
        with db.connect() as connection:
            connection.execute(
                "INSERT INTO shortlist (car_id) VALUES (?)",
                (existing_id,),
            )

    assert len(db.list_shortlist()) == 1