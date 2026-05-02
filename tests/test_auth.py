import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_student_signup_and_login():
    """Test 1: Student signup + login returns valid JWT"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Signup
        signup_response = await ac.post("/auth/signup", json={
            "name": "New Student",
            "email": "newstudent@test.com",
            "password": "test123",
            "role": "student",
            "institution_id": 1
        })
        assert signup_response.status_code == 200
        assert "access_token" in signup_response.json()
        
        # Login with same credentials
        login_response = await ac.post("/auth/login", json={
            "email": "newstudent@test.com",
            "password": "test123"
        })
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

@pytest.mark.asyncio
async def test_trainer_login():
    """Test trainer login works"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/login", json={
            "email": "trainer1@test.com",
            "password": "password123"
        })
        assert response.status_code == 200
        token = response.json().get("access_token")
        assert token is not None
        assert len(token) > 0

@pytest.mark.asyncio
async def test_invalid_login():
    """Test invalid login returns 401"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/login", json={
            "email": "wrong@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_signup_duplicate_email():
    """Test signup with existing email returns 400"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First signup
        await ac.post("/auth/signup", json={
            "name": "Test User",
            "email": "duplicate@test.com",
            "password": "test123",
            "role": "student"
        })
        
        # Duplicate signup
        response = await ac.post("/auth/signup", json={
            "name": "Test User 2",
            "email": "duplicate@test.com",
            "password": "test123",
            "role": "student"
        })
        assert response.status_code == 400
        assert "already registered" in response.json().get("detail", "").lower()