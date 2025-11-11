from fastapi.testclient import TestClient
import copy
import pytest

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def restore_activities():
    # backup global activities and restore after each test to keep tests isolated
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Known activity from the seeded data
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure the test email is not already present
    assert email not in app_module.activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Verify participant appears in the activities payload
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    assert email in resp2.json()[activity]["participants"]

    # Duplicate signup should fail with 400
    resp_dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp_dup.status_code == 400

    # Unregister
    resp_un = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp_un.status_code == 200
    assert "Unregistered" in resp_un.json()["message"]

    # Verify removed
    resp3 = client.get("/activities")
    assert email not in resp3.json()[activity]["participants"]

    # Unregistering again should return 400
    resp_un_again = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp_un_again.status_code == 400
