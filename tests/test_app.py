"""
Backend tests for the FastAPI High School Management System API.

Tests are structured using the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Perform the action being tested
- Assert: Verify the results
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all available activities.
        
        AAA Pattern:
        - Arrange: No setup needed, activities are pre-populated by fixture
        - Act: Make GET request to /activities
        - Assert: Response contains all activities with correct structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 4  # 3 pre-populated + 1 empty activity
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Empty Activity" in activities

    def test_get_activities_includes_participant_info(self, client):
        """
        Test that activities include participant details.
        
        AAA Pattern:
        - Arrange: Activities with known participants exist
        - Act: Fetch activities
        - Assert: Each activity includes participants list
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club = activities["Chess Club"]
        assert "participants" in chess_club
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 2

    def test_get_activities_includes_activity_metadata(self, client):
        """
        Test that activities include all required metadata fields.
        
        AAA Pattern:
        - Arrange: Activities exist with full metadata
        - Act: Fetch activities
        - Assert: Response contains description, schedule, max_participants
        """
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


class TestGetRoot:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        Test that GET / redirects to /static/index.html.
        
        AAA Pattern:
        - Arrange: No setup needed
        - Act: Make GET request to root
        - Assert: Response is a redirect (307) to static index
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_successful_signup_adds_participant(self, client):
        """
        Test that a student can successfully sign up for an activity.
        
        AAA Pattern:
        - Arrange: Empty Activity is available with 0 participants
        - Act: Sign up new student for Empty Activity
        - Assert: Response confirms signup, participant count increases to 1
        """
        # Arrange
        test_email = "newstudent@mergington.edu"
        activity_name = "Empty Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {test_email} for {activity_name}"
        
        # Verify participant was added by fetching activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 1

    def test_signup_returns_error_for_invalid_activity(self, client):
        """
        Test that signup fails with 404 when activity doesn't exist.
        
        AAA Pattern:
        - Arrange: Use a non-existent activity name
        - Act: Attempt signup for non-existent activity
        - Assert: Response is 404 with appropriate error message
        """
        # Arrange
        test_email = "student@mergington.edu"
        invalid_activity = "Non-Existent Club"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_duplicate_signup_returns_error(self, client):
        """
        Test that a student cannot sign up for the same activity twice (bug fix validation).
        
        AAA Pattern:
        - Arrange: Michael is already signed up for Chess Club
        - Act: Attempt to sign up Michael again for Chess Club
        - Assert: Response is 400 with duplicate signup error
        """
        # Arrange
        test_email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_multiple_students_can_signup(self, client):
        """
        Test that multiple different students can sign up for the same activity.
        
        AAA Pattern:
        - Arrange: Empty Activity has no participants
        - Act: Two different students sign up
        - Assert: Both are added to activity
        """
        # Arrange
        activity_name = "Empty Activity"
        email1 = "alice@mergington.edu"
        email2 = "bob@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants
        assert len(participants) == 2


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_successful_unregister_removes_participant(self, client):
        """
        Test that a participant can be successfully unregistered.
        
        AAA Pattern:
        - Arrange: Michael is registered for Chess Club
        - Act: Unregister Michael
        - Assert: Response confirms removal, participant count decreases
        """
        # Arrange
        activity_name = "Chess Club"
        test_email = "michael@mergington.edu"
        
        # Verify participant exists
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email in activities[activity_name]["participants"]
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {test_email} from {activity_name}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_returns_error_for_invalid_activity(self, client):
        """
        Test that unregister fails with 404 for non-existent activity.
        
        AAA Pattern:
        - Arrange: Use non-existent activity name
        - Act: Attempt to unregister from non-existent activity
        - Assert: Response is 404
        """
        # Arrange
        invalid_activity = "Non-Existent Club"
        test_email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants/{test_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_returns_error_for_non_participant(self, client):
        """
        Test that unregister fails with 400 when student is not registered.
        
        AAA Pattern:
        - Arrange: Emma is not registered for Gym Class
        - Act: Attempt to unregister Emma from Gym Class
        - Assert: Response is 400 with appropriate error
        """
        # Arrange
        activity_name = "Gym Class"
        test_email = "emma@mergington.edu"
        
        # Verify student is not in this activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email not in activities[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not registered for this activity"

    def test_multiple_participants_can_be_unregistered(self, client):
        """
        Test that multiple participants can be unregistered sequentially.
        
        AAA Pattern:
        - Arrange: Chess Club has two participants (michael, daniel)
        - Act: Unregister both participants
        - Assert: Both are removed, activity ends with 0 participants
        """
        # Arrange
        activity_name = "Chess Club"
        participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act & Assert for first removal
        response1 = client.delete(
            f"/activities/{activity_name}/participants/{participants[0]}"
        )
        assert response1.status_code == 200
        
        # Act & Assert for second removal
        response2 = client.delete(
            f"/activities/{activity_name}/participants/{participants[1]}"
        )
        assert response2.status_code == 200
        
        # Verify both are removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert len(activities[activity_name]["participants"]) == 0
