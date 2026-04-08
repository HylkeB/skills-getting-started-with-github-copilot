"""Pytest configuration and fixtures for the FastAPI application tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for making requests to the FastAPI app.
    
    Each test gets a fresh client instance to ensure test isolation.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Fixture that resets the activities database before each test.
    
    This ensures test isolation by providing a clean state for each test.
    The autouse=True parameter means this runs automatically before each test.
    """
    # Arrange: Set up fresh test data
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Empty Activity": {
            "description": "Activity with no participants",
            "schedule": "Mondays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        }
    })
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()
