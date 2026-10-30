import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = copy.deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Basketball Team"]["participants"] == []


def test_signup_adds_participant(client):
    email = "student@mergington.edu"

    response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Basketball Team"
    }
    assert email in client.get("/activities").json()["Basketball Team"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "student@mergington.edu"
    signup_url = "/activities/Basketball Team/signup"

    first_response = client.post(signup_url, params={"email": email})
    duplicate_response = client.post(signup_url, params={"email": email})

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == (
        "Student is already signed up for this activity"
    )
    assert client.get("/activities").json()["Basketball Team"]["participants"].count(email) == 1


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_removes_participant(client):
    email = "student@mergington.edu"
    client.post("/activities/Basketball Team/signup", params={"email": email})

    response = client.delete(
        "/activities/Basketball Team/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Basketball Team"}
    assert email not in client.get("/activities").json()["Basketball Team"]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Activity/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_returns_not_found_for_unknown_participant(client):
    response = client.delete(
        "/activities/Basketball Team/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404