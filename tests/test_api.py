"""
Unit tests for the Mergington High School API endpoints.
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that the root endpoint redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test the activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # We expect 9 activities
        
        # Check that expected activities are present
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Track and Field", "Drama Club", "Art Studio", "Debate Team", "Science Olympiad"
        ]
        for activity in expected_activities:
            assert activity in data

    def test_activity_structure(self, client, reset_activities):
        """Test that each activity has the correct structure."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestActivitySignup:
    """Test the activity signup functionality."""

    def test_signup_for_existing_activity(self, client, reset_activities, valid_email):
        """Test successful signup for an existing activity."""
        activity_name = "Chess Club"
        response = client.post(
            f"/activities/{activity_name}/signup",
            data={"email": valid_email}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == f"Signed up {valid_email} for {activity_name}"
        
        # Verify the student was actually added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert valid_email in activities_data[activity_name]["participants"]

    def test_signup_for_nonexistent_activity(self, client, valid_email):
        """Test signup for a nonexistent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            data={"email": valid_email}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Activity not found"

    def test_duplicate_signup_rejected(self, client, reset_activities):
        """Test that duplicate signup is rejected."""
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            data={"email": existing_email}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_with_url_encoded_activity_name(self, client, reset_activities, valid_email):
        """Test signup with URL-encoded activity names."""
        activity_name = "Track and Field"
        encoded_name = "Track%20and%20Field"
        
        response = client.post(
            f"/activities/{encoded_name}/signup",
            data={"email": valid_email}
        )
        
        assert response.status_code == status.HTTP_200_OK

    def test_signup_without_email(self, client):
        """Test signup without email returns 422."""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # HTTP_422_UNPROCESSABLE_CONTENT

    def test_signup_with_empty_email(self, client, reset_activities):
        """Test signup with empty email is accepted by the API."""
        response = client.post(
            "/activities/Chess Club/signup",
            data={"email": ""}
        )
        # The current API accepts empty strings, so this test verifies the actual behavior
        assert response.status_code == status.HTTP_200_OK


class TestActivityUnregistration:
    """Test the activity unregistration functionality."""

    def test_unregister_existing_participant(self, client, reset_activities):
        """Test successful unregistration of an existing participant."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify the student was actually removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistration from nonexistent activity returns 404."""
        email = "test@mergington.edu"
        response = client.delete(f"/activities/Nonexistent Activity/participants/{email}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_non_participant(self, client, reset_activities):
        """Test unregistration of someone not registered returns 400."""
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Student not registered for this activity"

    def test_unregister_with_url_encoded_names(self, client, reset_activities):
        """Test unregistration with URL-encoded activity and email."""
        activity_name = "Track%20and%20Field"
        email = "ryan%40mergington.edu"  # URL-encoded @
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        assert response.status_code == status.HTTP_200_OK


class TestIntegrationWorkflow:
    """Integration tests for complete workflows."""

    def test_signup_and_unregister_workflow(self, client, reset_activities, valid_email):
        """Test complete signup and unregister workflow."""
        activity_name = "Programming Class"
        
        # First, signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            data={"email": valid_email}
        )
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify signup in activities list
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert valid_email in activities_data[activity_name]["participants"]
        
        # Then, unregister
        unregister_response = client.delete(f"/activities/{activity_name}/participants/{valid_email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Verify removal from activities list
        final_activities_response = client.get("/activities")
        final_activities_data = final_activities_response.json()
        assert valid_email not in final_activities_data[activity_name]["participants"]

    def test_multiple_signups_for_same_student(self, client, reset_activities, valid_email):
        """Test that a student can sign up for multiple activities."""
        activities_to_join = ["Chess Club", "Programming Class", "Art Studio"]
        
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                data={"email": valid_email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity in activities_to_join:
            assert valid_email in activities_data[activity]["participants"]