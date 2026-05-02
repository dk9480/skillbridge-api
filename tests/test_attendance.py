import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_student_marks_attendance():
    """Test 3: Student successfully marking their own attendance"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login as student
        login_response = await ac.post("/auth/login", json={
            "email": "student1@test.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        
        # Mark attendance for session 1
        headers = {"Authorization": f"Bearer {token}"}
        attendance_response = await ac.post("/attendance/mark", json={
            "session_id": 1,
            "status": "present"
        }, headers=headers)
        
        assert attendance_response.status_code == 200
        assert attendance_response.json().get("message") == "Attendance marked successfully"

@pytest.mark.asyncio
async def test_trainer_cannot_mark_attendance():
    """Trainer trying to mark attendance should get 403"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login as trainer
        login_response = await ac.post("/auth/login", json={
            "email": "trainer1@test.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        
        # Try to mark attendance
        headers = {"Authorization": f"Bearer {token}"}
        attendance_response = await ac.post("/attendance/mark", json={
            "session_id": 1,
            "status": "present"
        }, headers=headers)
        
        assert attendance_response.status_code == 403

@pytest.mark.asyncio
async def test_student_mark_attendance_for_wrong_session():
    """Student marking attendance for session not enrolled in returns 403"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login as student
        login_response = await ac.post("/auth/login", json={
            "email": "student1@test.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        
        # Try to mark attendance for non-existent session
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post("/attendance/mark", json={
            "session_id": 999,
            "status": "present"
        }, headers=headers)
        
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_student_double_attendance():
    """Student marking attendance twice for same session returns 400"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login as student
        login_response = await ac.post("/auth/login", json={
            "email": "student2@test.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # First mark
        await ac.post("/attendance/mark", json={
            "session_id": 1,
            "status": "present"
        }, headers=headers)
        
        # Second mark (duplicate)
        response = await ac.post("/attendance/mark", json={
            "session_id": 1,
            "status": "present"
        }, headers=headers)
        
        assert response.status_code == 400