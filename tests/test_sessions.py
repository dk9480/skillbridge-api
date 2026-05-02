import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_trainer_creates_session():
    """Test 2: Trainer creating a session with all required fields"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First login as trainer
        login_response = await ac.post("/auth/login", json={
            "email": "trainer1@test.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        
        # Create session
        headers = {"Authorization": f"Bearer {token}"}
        session_response = await ac.post("/sessions", json={
            "batch_id": 1,
            "title": "Python Basics",
            "date": "2026-05-15",
            "start_time": "10:00",
            "end_time": "12:00"
        }, headers=headers)
        
        assert session_response.status_code == 200
        assert "session_id" in session_response.json()

@pytest.mark.asyncio
async def test_student_cannot_create_session():
    """Student trying to create session should get 403"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login as student
        login_response = await ac.post("/auth/login", json={
            "email": "student1@test.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        
        # Try to create session
        headers = {"Authorization": f"Bearer {token}"}
        session_response = await ac.post("/sessions", json={
            "batch_id": 1,
            "title": "Python Basics",
            "date": "2026-05-15",
            "start_time": "10:00",
            "end_time": "12:00"
        }, headers=headers)
        
        assert session_response.status_code == 403

@pytest.mark.asyncio
async def test_create_session_missing_fields():
    """Create session with missing fields returns 422"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login as trainer
        login_response = await ac.post("/auth/login", json={
            "email": "trainer1@test.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        
        # Try to create session with missing title
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post("/sessions", json={
            "batch_id": 1,
            "date": "2026-05-15",
            "start_time": "10:00",
            "end_time": "12:00"
        }, headers=headers)
        
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_trainer_get_session_attendance():
    """Trainer can view attendance for their session"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login as trainer
        login_response = await ac.post("/auth/login", json={
            "email": "trainer1@test.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        
        # Get attendance
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/sessions/1/attendance", headers=headers)
        
        assert response.status_code == 200
        assert "attendance" in response.json()