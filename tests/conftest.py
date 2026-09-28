#CHECKPOINT 14 automate the backend checks using temporary databases.
"""Provide isolated database files and HTTP clients for tests."""

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


@pytest.fixture
def database(tmp_path, monkeypatch):
    """Redirect database operations to a temporary file for this test."""
    test_path = tmp_path / "test-catalogue.db"

    # Replace the module attribute temporarily.
    # Pytest restores the original value when this test finishes.
    monkeypatch.setattr(db, "DATABASE_PATH", test_path)

    return test_path


@pytest.fixture
def client(database):
    """Start the application against this test's temporary database."""
    # Entering the context runs the application's startup lifespan.
    # Our initializer therefore creates and seeds the temporary database.
    with TestClient(app) as test_client:
        yield test_client

    # Leaving the context runs application shutdown.


@pytest.fixture
def example_car():
    """Return fresh, valid input for tests that create a car."""
    return {
        "name": "Test Coupe",
        "category": "Coupe",
        "manufacturer": "Toyota",
        "variant": "Testing Edition",
        "description": (
            "A sample coupe used to verify that the catalogue's "
            "API and database work together."
        ),
        "tip": "Check the seat adjustment before driving.",
    }