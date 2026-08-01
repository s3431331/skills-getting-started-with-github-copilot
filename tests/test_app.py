import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = copy.deepcopy(original)


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["description"].startswith("Learn strategies")


def test_signup_for_activity_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 200
    assert "newstudent@mergington.edu" in app_module.activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"


def test_duplicate_signup_returns_400(client):
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "alreadyhere@mergington.edu"},
    )

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "alreadyhere@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_unregister_participant_removes_email(client):
    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")

    assert response.status_code == 200
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"


def test_unregister_missing_participant_returns_404(client):
    response = client.delete("/activities/Chess Club/participants/notfound@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
