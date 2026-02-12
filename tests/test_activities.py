"""Tests for activities API endpoints."""
import pytest


def test_get_activities(client):
    """Test fetching all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert len(activities) > 0


def test_activity_structure(client):
    """Test that activities have the expected structure."""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, details in activities.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity."""
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity_name in result["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_email(client):
    """Test that signing up with the same email fails."""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up
    
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"].lower()


def test_signup_nonexistent_activity(client):
    """Test signup for a non-existent activity."""
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"].lower()


def test_unregister_participant_success(client):
    """Test successfully unregistering a participant."""
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already signed up
    
    # Verify participant is registered
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    
    assert unregister_response.status_code == 200
    result = unregister_response.json()
    assert "message" in result
    assert "Unregistered" in result["message"]
    
    # Verify participant was removed
    final_response = client.get("/activities")
    final_activities = final_response.json()
    assert email not in final_activities[activity_name]["participants"]


def test_unregister_nonexistent_participant(client):
    """Test unregistering a participant not in the activity."""
    activity_name = "Chemistry Club"  # Activity doesn't exist, or student not in it
    email = "nonexistent@mergington.edu"
    
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    
    # Should fail because activity doesn't exist
    assert response.status_code == 404


def test_unregister_from_nonexistent_activity(client):
    """Test unregistering from a non-existent activity."""
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"].lower()


def test_root_redirect(client):
    """Test that root path redirects to static index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]
