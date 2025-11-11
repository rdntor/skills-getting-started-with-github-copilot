from fastapi.testclient import TestClient
import pytest
from src.app import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def test_activity():
    """Sample activity data for testing"""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["test1@mergington.edu", "test2@mergington.edu"]
        }
    }

def test_read_activities(client):
    """Test GET /activities endpoint"""
    response = client.get("/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    # Check some known activities exist
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify activity structure
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)

def test_signup_for_activity(client):
    """Test POST /activities/{activity_name}/signup endpoint"""
    activity_name = "Chess Club"
    test_email = "new.student@mergington.edu"
    
    # Try to sign up
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify student was added by getting activities
    activities = client.get("/activities").json()
    assert test_email in activities[activity_name]["participants"]

def test_signup_duplicate(client):
    """Test signing up an already registered student fails"""
    activity_name = "Chess Club"
    # Use an email we know is already registered from the initial data
    test_email = "michael@mergington.edu"
    
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )
    assert response.status_code == 400
    assert "detail" in response.json()

def test_unregister_from_activity(client):
    """Test DELETE /activities/{activity_name}/participants endpoint"""
    activity_name = "Chess Club"
    test_email = "michael@mergington.edu"  # Using a known participant
    
    # Try to unregister
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": test_email}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify student was removed
    activities = client.get("/activities").json()
    assert test_email not in activities[activity_name]["participants"]

def test_unregister_not_found(client):
    """Test unregistering a non-existent participant fails"""
    activity_name = "Chess Club"
    test_email = "not.registered@mergington.edu"
    
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": test_email}
    )
    assert response.status_code == 404
    assert "detail" in response.json()