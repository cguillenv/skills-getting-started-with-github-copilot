import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def _activity_signup_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup"


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_all_options():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()

    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant_and_prevents_duplicates():
    email = "new_student@mergington.edu"

    signup_response = client.post(_activity_signup_path("Chess Club"), params={"email": email})
    assert signup_response.status_code == 200
    assert email in activities["Chess Club"]["participants"]

    duplicate_response = client.post(_activity_signup_path("Chess Club"), params={"email": email})
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant_and_handles_missing():
    email = "michael@mergington.edu"
    assert email in activities["Chess Club"]["participants"]

    delete_response = client.delete(_activity_signup_path("Chess Club"), params={"email": email})
    assert delete_response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]

    missing_response = client.delete(_activity_signup_path("Chess Club"), params={"email": email})
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Student not registered for this activity"
