"""
Tests for the High School Management System API

Tests for all endpoints including:
- GET /activities - retrieve all activities
- POST /activities/{activity_name}/signup - sign up for an activity
- DELETE /activities/{activity_name}/signup - unregister from an activity
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        """Test that GET /activities returns all available activities"""
        # Arrange
        expected_keys = ["Chess Club", "Programming Class", "Basketball Team"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        for key in expected_keys:
            assert key in activities
    
    def test_activity_has_required_fields(self):
        """Test that each activity has all required fields"""
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_existing_activity(self):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_for_nonexistent_activity(self):
        """Test that signup fails for non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered_student(self):
        """Test that a student cannot sign up twice for the same activity"""
        # Arrange
        activity_name = "Soccer Club"
        email = "duplicate@mergington.edu"
        
        # Act - First signup should succeed
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # Assert first signup
        assert response1.status_code == 200
        
        # Act - Second signup should fail
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert second signup fails
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_from_activity(self):
        """Test successful unregistration from an activity"""
        # Arrange
        activity_name = "Art Club"
        email = "unregister@mergington.edu"
        
        # First sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_from_nonexistent_activity(self):
        """Test that unregister fails for non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered_student(self):
        """Test that unregister fails if student is not registered"""
        # Arrange
        activity_name = "Drama Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestRootRedirect:
    """Test suite for GET / endpoint"""
    
    def test_root_redirects_to_static(self):
        """Test that root path redirects to /static/index.html"""
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"