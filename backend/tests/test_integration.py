import pytest
import pytest_asyncio
from httpx import AsyncClient

# Global state to pass data between tests (simplistic for this flow)
test_data = {
    "org_name": "testorg",
    "email": "admin@testorg.com",
    "password": "SecurePassword123!",
    "token": None
}

@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Service is running"}

@pytest.mark.asyncio
async def test_create_org(client: AsyncClient):
    response = await client.post("/org/create", json={
        "organization_name": test_data["org_name"],
        "email": test_data["email"],
        "password": test_data["password"]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["ok"] is True
    assert data["organization"]["organization_name"] == test_data["org_name"]

@pytest.mark.asyncio
async def test_create_org_duplicate(client: AsyncClient):
    response = await client.post("/org/create", json={
        "organization_name": test_data["org_name"],
        "email": "other@test.com",
        "password": "pass"
    })
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_admin_login(client: AsyncClient):
    response = await client.post("/admin/login", json={
        "email": test_data["email"],
        "password": test_data["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    test_data["token"] = data["access_token"]

@pytest.mark.asyncio
async def test_get_org_authenticated(client: AsyncClient):
    # This endpoint is currently public in logic but let's assume we want to test data correctness
    response = await client.get(f"/org/get?organization_name={test_data['org_name']}")
    assert response.status_code == 200
    data = response.json()
    assert data["organization"]["organization_name"] == test_data["org_name"]

@pytest.mark.asyncio
async def test_rename_org(client: AsyncClient):
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    new_name = "testorg_renamed"
    response = await client.put("/org/update", headers=headers, json={
        "organization_name": test_data["org_name"],
        "new_organization_name": new_name
    })
    assert response.status_code == 200
    data = response.json()
    assert data["organization"]["organization_name"] == new_name
    
    # Update test_data for cleanup
    test_data["org_name"] = new_name

@pytest.mark.asyncio
async def test_delete_org(client: AsyncClient):
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = await client.request("DELETE", "/org/delete", headers=headers, json={
        "organization_name": test_data["org_name"]
    })
    assert response.status_code == 200
    assert response.json()["ok"] is True

    # Verify gone
    response = await client.get(f"/org/get?organization_name={test_data['org_name']}")
    assert response.status_code == 404
