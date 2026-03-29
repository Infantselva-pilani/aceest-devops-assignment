"""
ACEest Fitness & Gym - Pytest Test Suite
Tests for all Flask API endpoints
Student Roll No: 2024TM93572
"""

import pytest
import json
import os
import sys

# Ensure app is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use a separate test database
os.environ["DB_NAME"] = "test_aceest.db"

from app import app, init_db


@pytest.fixture(scope="module")
def client():
    """Set up Flask test client with a fresh test database."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        with app.app_context():
            init_db()
        yield c

    # Cleanup test DB after all tests
    if os.path.exists("test_aceest.db"):
        os.remove("test_aceest.db")


# ---------- HEALTH CHECK ----------
class TestHealth:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "service" in data


# ---------- CLIENT TESTS ----------
class TestClients:
    def test_get_clients_empty(self, client):
        response = client.get("/clients")
        assert response.status_code == 200
        assert json.loads(response.data) == []

    def test_add_client_success(self, client):
        payload = {"name": "Alice Johnson", "age": 28, "weight": 65.0, "program": "Fat Loss"}
        response = client.post("/clients", json=payload)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "Alice Johnson"
        assert data["membership_status"] == "Active"

    def test_add_client_missing_name(self, client):
        response = client.post("/clients", json={"age": 25})
        assert response.status_code == 400

    def test_add_client_empty_name(self, client):
        response = client.post("/clients", json={"name": "   "})
        assert response.status_code == 400

    def test_add_duplicate_client(self, client):
        client.post("/clients", json={"name": "Bob Smith"})
        response = client.post("/clients", json={"name": "Bob Smith"})
        assert response.status_code == 409

    def test_get_clients_returns_list(self, client):
        response = client.get("/clients")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_single_client(self, client):
        client.post("/clients", json={"name": "Carol White"})
        response = client.get("/clients/Carol White")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Carol White"

    def test_get_nonexistent_client(self, client):
        response = client.get("/clients/NonExistent Person")
        assert response.status_code == 404

    def test_update_client(self, client):
        client.post("/clients", json={"name": "Dave Brown", "age": 30})
        response = client.put("/clients/Dave Brown", json={"age": 31, "program": "Muscle Gain"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["age"] == 31
        assert data["program"] == "Muscle Gain"

    def test_update_nonexistent_client(self, client):
        response = client.put("/clients/Ghost Person", json={"age": 25})
        assert response.status_code == 404

    def test_delete_client(self, client):
        client.post("/clients", json={"name": "ToDelete User"})
        response = client.delete("/clients/ToDelete User")
        assert response.status_code == 200
        # Verify it's gone
        get_response = client.get("/clients/ToDelete User")
        assert get_response.status_code == 404

    def test_delete_nonexistent_client(self, client):
        response = client.delete("/clients/Nobody Here")
        assert response.status_code == 404


# ---------- WORKOUT TESTS ----------
class TestWorkouts:
    def test_add_workout_success(self, client):
        client.post("/clients", json={"name": "Workout Tester"})
        payload = {
            "client_name": "Workout Tester",
            "date": "2025-01-15",
            "workout_type": "Strength",
            "duration_min": 60,
            "notes": "Great session"
        }
        response = client.post("/workouts", json=payload)
        assert response.status_code == 201

    def test_add_workout_missing_client(self, client):
        response = client.post("/workouts", json={"workout_type": "Cardio"})
        assert response.status_code == 400

    def test_get_workouts(self, client):
        response = client.get("/workouts/Workout Tester")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_workouts_empty_client(self, client):
        client.post("/clients", json={"name": "No Workouts"})
        response = client.get("/workouts/No Workouts")
        assert response.status_code == 200
        assert json.loads(response.data) == []


# ---------- PROGRESS TESTS ----------
class TestProgress:
    def test_add_progress_success(self, client):
        client.post("/clients", json={"name": "Progress Tester"})
        payload = {"client_name": "Progress Tester", "week": "Week 1", "adherence": 85}
        response = client.post("/progress", json=payload)
        assert response.status_code == 201

    def test_add_progress_invalid_adherence_over_100(self, client):
        payload = {"client_name": "Progress Tester", "week": "Week 2", "adherence": 150}
        response = client.post("/progress", json=payload)
        assert response.status_code == 400

    def test_add_progress_invalid_adherence_negative(self, client):
        payload = {"client_name": "Progress Tester", "week": "Week 3", "adherence": -10}
        response = client.post("/progress", json=payload)
        assert response.status_code == 400

    def test_get_progress(self, client):
        response = client.get("/progress/Progress Tester")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["adherence"] == 85

    def test_add_progress_missing_client_name(self, client):
        response = client.post("/progress", json={"week": "Week 1", "adherence": 70})
        assert response.status_code == 400


# ---------- MEMBERSHIP TESTS ----------
class TestMembership:
    def test_check_membership_active(self, client):
        client.post("/clients", json={"name": "Member Test", "membership_status": "Active"})
        response = client.get("/membership/Member Test")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["membership_status"] == "Active"

    def test_check_membership_not_found(self, client):
        response = client.get("/membership/Unknown Member")
        assert response.status_code == 404


# ---------- PROGRAM GENERATOR TESTS ----------
class TestProgramGenerator:
    def test_generate_fat_loss_program(self, client):
        response = client.post("/generate-program", json={"goal": "Fat Loss"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["goal"] == "Fat Loss"
        assert len(data["recommended_programs"]) > 0

    def test_generate_muscle_gain_program(self, client):
        response = client.post("/generate-program", json={"goal": "Muscle Gain"})
        assert response.status_code == 200

    def test_generate_beginner_program(self, client):
        response = client.post("/generate-program", json={"goal": "Beginner"})
        assert response.status_code == 200

    def test_generate_unknown_goal(self, client):
        response = client.post("/generate-program", json={"goal": "Flying"})
        assert response.status_code == 400

    def test_generate_program_default_goal(self, client):
        response = client.post("/generate-program", json={})
        assert response.status_code == 200
