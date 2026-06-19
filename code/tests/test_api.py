import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_event_type(client: AsyncClient, auth_token: str) -> None:
    response = await client.post(
        "/api/v1/event-types",
        json={
            "title": "Consultation",
            "slug": "consult",
            "length": 30,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Consultation"
    assert data["slug"] == "consult"
    assert data["length"] == 30
    assert data["owner_username"] == "demo"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_event_types(client: AsyncClient, auth_token: str) -> None:
    response = await client.get(
        "/api/v1/event-types",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
