import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_protected_endpoint_no_token_returns_401():
    """Test 5: Request to protected endpoint with no token returns 401"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Try to access protected endpoint without token
        response = await ac.get("/batches/1/summary")
        assert response.status_code == 401
        
        # Try to create batch without token
        create_response = await ac.post("/batches", json={
            "name": "Test Batch",
            "institution_id": 1
        })
        assert create_response.status_code == 401

@pytest.mark.asyncio
async def test_invalid_token_returns_401():
    """Request with invalid token returns 401"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": "Bearer invalid-token-12345"}
        response = await ac.get("/batches/1/summary", headers=headers)
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_wrong_role_returns_403():
    """Student trying to access trainer endpoint returns 403"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login as student
        login_response = await ac.post("/auth/login", json={
            "email": "student1@test.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        
        # Try to access trainer-only endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/sessions/1/attendance", headers=headers)
        
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_institution_access_batch_summary():
    """Institution can access batch summary for their batch"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login as institution
        login_response = await ac.post("/auth/login", json={
            "email": "inst_a@test.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        
        # Access batch summary
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/batches/1/summary", headers=headers)
        
        # Should work (batch 1 belongs to institution A)
        assert response.status_code == 200
        assert "total_students" in response.json()

@pytest.mark.asyncio
async def test_malformed_token_returns_401():
    """Request with malformed Authorization header returns 401"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Wrong format (missing Bearer)
        headers = {"Authorization": "justthetoken"}
        response = await ac.get("/batches/1/summary", headers=headers)
        assert response.status_code == 401
        
        # Empty header
        headers = {"Authorization": ""}
        response = await ac.get("/batches/1/summary", headers=headers)
        assert response.status_code == 401