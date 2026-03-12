import copy
from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)

# make an immutable copy of the original activities state so tests can reset it
_original_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def restore_activities():
    """Reset the in-memory activities dictionary before each test."""
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


def test_root_redirect():
    # Arrange: nothing to set up

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    # the root should serve index.html from the static directory
    assert "text/html" in response.headers["content-type"]


def test_get_activities():
    # Arrange: use the reset activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == _original_activities


def test_signup_for_activity_success():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_nonexistent_activity():
    # Arrange: use a name that isn't in the list
    bogus = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{bogus}/signup", params={"email": "x@x.com"})

    # Assert
    assert response.status_code == 404


def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    email = _original_activities[activity]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
