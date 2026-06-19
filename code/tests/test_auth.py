import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth",
        json={
            "username": "demo",
            "email": "other@example.com",
            "password": "securepass",
        },
    )
    assert response.status_code == 409
    assert "Username already taken" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "demo", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "demo", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient, auth_token: str) -> None:
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "demo"
    assert data["email"] == "demo@example.com"


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
