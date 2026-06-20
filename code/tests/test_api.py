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
async def test_create_event_type_duplicate_slug(
    client: AsyncClient, auth_token: str
) -> None:
    payload = {
        "title": "Consultation",
        "slug": "consult",
        "length": 30,
    }
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post("/api/v1/event-types", json=payload, headers=headers)
    assert response.status_code == 201

    response = await client.post("/api/v1/event-types", json=payload, headers=headers)
    assert response.status_code == 409
    assert "slug" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_event_types(client: AsyncClient, auth_token: str) -> None:
    response = await client.get(
        "/api/v1/event-types",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_update_event_type(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_resp = await client.post(
        "/api/v1/event-types",
        json={"title": "Original", "slug": "original", "length": 30},
        headers=headers,
    )
    et_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/event-types/{et_id}",
        json={"title": "Updated Title", "length": 60},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["length"] == 60
    assert data["slug"] == "original"


@pytest.mark.asyncio
async def test_update_event_type_not_found(
    client: AsyncClient, auth_token: str
) -> None:
    response = await client.patch(
        "/api/v1/event-types/99999",
        json={"title": "Nope"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_event_type_no_fields(
    client: AsyncClient, auth_token: str
) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_resp = await client.post(
        "/api/v1/event-types",
        json={"title": "No Fields", "slug": "no-fields", "length": 30},
        headers=headers,
    )
    et_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/event-types/{et_id}",
        json={},
        headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_event_type(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_resp = await client.post(
        "/api/v1/event-types",
        json={"title": "To Delete", "slug": "to-delete", "length": 30},
        headers=headers,
    )
    et_id = create_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/event-types/{et_id}", headers=headers
    )
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/event-types/{et_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_event_type_not_found(
    client: AsyncClient, auth_token: str
) -> None:
    response = await client.delete(
        "/api/v1/event-types/99999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_schedule(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post(
        "/api/v1/schedules",
        json={"name": "Working Hours", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Working Hours"
    assert data["time_zone"] == "Europe/Moscow"
    assert "id" in data
    assert data["availability"] == []


@pytest.mark.asyncio
async def test_list_schedules(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    await client.post(
        "/api/v1/schedules",
        json={"name": "Work", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    response = await client.get("/api/v1/schedules", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_schedule(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_resp = await client.post(
        "/api/v1/schedules",
        json={"name": "My Schedule", "time_zone": "Europe/London"},
        headers=headers,
    )
    schedule_id = create_resp.json()["id"]

    response = await client.get(
        f"/api/v1/schedules/{schedule_id}", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "My Schedule"


@pytest.mark.asyncio
async def test_update_schedule(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_resp = await client.post(
        "/api/v1/schedules",
        json={"name": "Old Name", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    schedule_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/schedules/{schedule_id}",
        json={"name": "New Name"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["time_zone"] == "Europe/Moscow"


@pytest.mark.asyncio
async def test_delete_schedule(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_resp = await client.post(
        "/api/v1/schedules",
        json={"name": "To Delete", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    schedule_id = create_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/schedules/{schedule_id}", headers=headers
    )
    assert response.status_code == 204

    get_resp = await client.get(
        f"/api/v1/schedules/{schedule_id}", headers=headers
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_schedule_not_found(
    client: AsyncClient, auth_token: str
) -> None:
    response = await client.delete(
        "/api/v1/schedules/99999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_availability(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    sched_resp = await client.post(
        "/api/v1/schedules",
        json={"name": "Work", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    schedule_id = sched_resp.json()["id"]

    response = await client.post(
        f"/api/v1/schedules/{schedule_id}/availability",
        json={
            "days": "[0,1,2,3,4]",
            "start_time": "09:00",
            "end_time": "17:00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["days"] == "[0,1,2,3,4]"
    assert "id" in data


@pytest.mark.asyncio
async def test_delete_availability(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    sched_resp = await client.post(
        "/api/v1/schedules",
        json={"name": "Work", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    schedule_id = sched_resp.json()["id"]

    avail_resp = await client.post(
        f"/api/v1/schedules/{schedule_id}/availability",
        json={
            "days": "[0,1,2,3,4]",
            "start_time": "09:00",
            "end_time": "17:00",
        },
    )
    avail_id = avail_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/schedules/{schedule_id}/availability/{avail_id}",
    )
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/schedules/{schedule_id}", headers=headers)
    avail_count = len(get_resp.json()["availability"])
    assert avail_count == 0


@pytest.mark.asyncio
async def test_update_availability(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    sched_resp = await client.post(
        "/api/v1/schedules",
        json={"name": "Work", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    schedule_id = sched_resp.json()["id"]

    avail_resp = await client.post(
        f"/api/v1/schedules/{schedule_id}/availability",
        json={
            "days": "[0,1,2,3,4]",
            "start_time": "09:00",
            "end_time": "17:00",
        },
    )
    avail_id = avail_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/schedules/{schedule_id}/availability/{avail_id}",
        json={"start_time": "10:00", "end_time": "18:00"},
    )
    assert response.status_code == 200
    assert response.json()["start_time"] == "10:00"
    assert response.json()["end_time"] == "18:00"
