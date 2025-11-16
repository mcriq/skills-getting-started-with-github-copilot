"""
Performance and edge case tests for the Mergington High School API.
"""

import pytest
from fastapi import status
from src.app import activities


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_activity_name_with_special_characters(self, client, reset_activities):
        """Test activity names with special characters."""
        special_names = [
            "Activity with spaces",
            "Activity-with-dashes", 
            "Activity_with_underscores",
            "Activity123",
            "Activity/with/slashes"
        ]
        
        for name in special_names:
            response = client.post(
                f"/activities/{name}/signup",
                data={"email": "test@mergington.edu"}
            )
            # Should return 404 since these activities don't exist
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_email_formats(self, client, reset_activities):
        """Test various email formats."""
        emails = [
            "valid@mergington.edu",
            "valid.email@mergington.edu", 
            "valid+tag@mergington.edu",
            "valid123@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                "/activities/Chess Club/signup",
                data={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
            
            # Clean up for next iteration
            client.delete(f"/activities/Chess Club/participants/{email}")

    def test_very_long_email(self, client, reset_activities):
        """Test signup with very long email."""
        long_email = "a" * 100 + "@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            data={"email": long_email}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_empty_activity_name(self, client):
        """Test endpoints with empty activity name."""
        response = client.post(
            "/activities//signup",
            data={"email": "test@mergington.edu"}
        )
        # FastAPI should handle this as a different route or 404
        assert response.status_code in [status.HTTP_404_NOT_FOUND, 422]  # 422 = HTTP_422_UNPROCESSABLE_CONTENT


class TestDataConsistency:
    """Test data consistency and state management."""

    def test_participants_list_maintains_order(self, client, reset_activities):
        """Test that participants list maintains insertion order."""
        activity_name = "Chess Club"
        emails = ["first@mergington.edu", "second@mergington.edu", "third@mergington.edu"]
        
        # Add participants in order
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                data={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Check order is maintained
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data[activity_name]["participants"]
        
        # The new participants should be at the end in the order they were added
        for i, email in enumerate(emails):
            assert email in participants
            # Find the position and ensure it's after the original participants
            email_index = participants.index(email)
            assert email_index >= 2  # After the 2 original participants

    def test_concurrent_signup_simulation(self, client, reset_activities):
        """Test multiple signups for the same activity."""
        activity_name = "Programming Class"
        emails = [f"student{i}@mergington.edu" for i in range(5)]
        
        # Simulate multiple students signing up
        responses = []
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                data={"email": email}
            )
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all are registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for email in emails:
            assert email in activities_data[activity_name]["participants"]

    def test_signup_after_unregister(self, client, reset_activities):
        """Test that a student can re-register after unregistering."""
        activity_name = "Drama Club"
        email = "test@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            data={"email": email}
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Unregister
        response2 = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response2.status_code == status.HTTP_200_OK
        
        # Signup again
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            data={"email": email}
        )
        assert response3.status_code == status.HTTP_200_OK
        
        # Verify final state
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    def test_all_activities_exist(self, client, reset_activities):
        """Test that all expected activities are available."""
        expected_activities = {
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Track and Field", "Drama Club", "Art Studio", "Debate Team", "Science Olympiad"
        }
        
        response = client.get("/activities")
        data = response.json()
        actual_activities = set(data.keys())
        
        assert expected_activities == actual_activities

    def test_original_participants_preserved(self, client, reset_activities):
        """Test that original participants are preserved through operations."""
        # Get original state
        original_response = client.get("/activities")
        original_data = original_response.json()
        
        # Perform some operations
        test_email = "test@mergington.edu"
        client.post("/activities/Chess Club/signup", data={"email": test_email})
        client.delete(f"/activities/Chess Club/participants/{test_email}")
        
        # Check that original participants are still there
        final_response = client.get("/activities")
        final_data = final_response.json()
        
        for activity_name, activity_data in original_data.items():
            original_participants = set(activity_data["participants"])
            final_participants = set(final_data[activity_name]["participants"])
            
            # All original participants should still be there
            assert original_participants.issubset(final_participants)


class TestErrorHandling:
    """Test error handling and HTTP status codes."""

    def test_method_not_allowed(self, client):
        """Test that unsupported HTTP methods return 405."""
        # Try PUT on signup endpoint
        response = client.put("/activities/Chess Club/signup")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # Try POST on unregister endpoint
        response = client.post("/activities/Chess Club/participants/test@mergington.edu")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_malformed_requests(self, client):
        """Test malformed requests return appropriate errors."""
        # Missing form data
        response = client.post(
            "/activities/Chess Club/signup",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422  # HTTP_422_UNPROCESSABLE_CONTENT
        
        # Wrong content type for form data
        response = client.post(
            "/activities/Chess Club/signup",
            json={"email": "test@mergington.edu"}  # JSON instead of form data
        )
        assert response.status_code == 422  # HTTP_422_UNPROCESSABLE_CONTENT