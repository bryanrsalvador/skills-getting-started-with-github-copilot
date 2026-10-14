import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def activity_store(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn and play chess",
            "schedule": "Fridays, 3:30 PM",
            "max_participants": 4,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activity_store):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, activity_store):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activity_store


def test_signup_adds_participant(client, activity_store):
    email = "student@mergington.edu"

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activity_store["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, activity_store):
    email = "existing@mergington.edu"

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activity_store["Chess Club"]["participants"] == [email]


def test_signup_returns_404_for_unknown_activity(client, activity_store):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_store["Chess Club"]["participants"] == ["existing@mergington.edu"]


def test_unregister_removes_participant(client, activity_store):
    email = "existing@mergington.edu"

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert activity_store["Chess Club"]["participants"] == []


def test_unregister_returns_404_for_missing_participant(client, activity_store):
    participants_before = activity_store["Chess Club"]["participants"].copy()

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activity_store["Chess Club"]["participants"] == participants_before


def test_unregister_returns_404_for_unknown_activity(client, activity_store):
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_store["Chess Club"]["participants"] == ["existing@mergington.edu"]
