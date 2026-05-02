import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_monitoring_endpoint_returns_405_for_post():
    """Test 4: POST to /monitoring/attendance returning 405"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test POST
        post_response = await ac.post("/monitoring/attendance")
        assert post_response.status_code == 405
        
        # Test PUT
        put_response = await ac.put("/monitoring/attendance")
        assert put_response.status_code == 405
        
        # Test DELETE
        delete_response = await ac.delete("/monitoring/attendance")
        assert delete_response.status_code == 405
        
        # Test PATCH
        patch_response = await ac.patch("/monitoring/attendance")
        assert patch_response.status_code == 405

@pytest.mark.asyncio
async def test_monitoring_endpoint_get_requires_auth():
    """GET to /monitoring/attendance without token returns 401"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/monitoring/attendance")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_monitoring_endpoint_with_normal_token_returns_403():
    """GET to /monitoring/attendance with normal JWT returns 403"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login as monitoring officer (get normal token)
        login_response = await ac.post("/auth/login", json={
            "email": "mo@test.com",
            "password": "password123"
        })
        normal_token = login_response.json().get("access_token")
        
        # Try to access monitoring endpoint with normal token
        headers = {"Authorization": f"Bearer {normal_token}"}
        response = await ac.get("/monitoring/attendance", headers=headers)
        
        # Should fail because need special monitoring token
        assert response.status_code == 403