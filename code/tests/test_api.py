from datetime import date, datetime, timedelta, time
from unittest.mock import patch
from zoneinfo import ZoneInfo

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


def _next_weekday(weekday: int) -> date:
    today = date.today()
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


NEXT_MONDAY = _next_weekday(0)
FIXED_NOW = datetime.combine(NEXT_MONDAY, time(8, 0), tzinfo=ZoneInfo("Europe/London"))


class _MockSlotsDatetime:
    @classmethod
    def now(cls, tz=None):
        if tz is not None:
            return FIXED_NOW.astimezone(tz)
        return FIXED_NOW.replace(tzinfo=None)

    @classmethod
    def combine(cls, *args, **kwargs):  # noqa: N805
        return datetime.combine(*args, **kwargs)

    @classmethod
    def timedelta(cls, *args, **kwargs):  # noqa: N805
        return __import__("datetime").timedelta(*args, **kwargs)


@pytest.mark.asyncio
async def test_slots_minimum_booking_notice(client: AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}

    with patch("app.api.slots.datetime", _MockSlotsDatetime):
        sched_resp = await client.post(
            "/api/v1/schedules",
            json={"name": "Work", "time_zone": "Europe/London"},
            headers=headers,
        )
        schedule_id = sched_resp.json()["id"]

        await client.post(
            f"/api/v1/schedules/{schedule_id}/availability",
            json={"days": "[0]", "start_time": "09:00", "end_time": "17:00"},
        )

        et_resp = await client.post(
            "/api/v1/event-types",
            json={
                "title": "Consult",
                "slug": "consult",
                "length": 30,
                "slot_interval": 30,
                "minimum_booking_notice": 120,
                "schedule_id": schedule_id,
            },
            headers=headers,
        )
        assert et_resp.status_code == 201

        response = await client.get(
            f"/api/v1/demo/consult/slots?date={NEXT_MONDAY.isoformat()}&timezone=Europe/London"
        )
        assert response.status_code == 200
        data = response.json()
        slot_times = [datetime.fromisoformat(s["time"]).astimezone(ZoneInfo("Europe/London")) for s in data["slots"]]

        # now=08:00, min_bookable = 08:00 + 120min = 10:00
        # Slots 09:00, 09:30 excluded → 14 slots (10:00-16:30, interval 30min)
        assert len(data["slots"]) == 14

        for st in slot_times:
            assert st.hour >= 10


@pytest.mark.asyncio
async def test_slots_buffers_exclude_overlapping_slots(
    client: AsyncClient, auth_token: str
) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}

    with patch("app.api.slots.datetime", _MockSlotsDatetime):
        sched_resp = await client.post(
            "/api/v1/schedules",
            json={"name": "Work", "time_zone": "Europe/London"},
            headers=headers,
        )
        schedule_id = sched_resp.json()["id"]

        await client.post(
            f"/api/v1/schedules/{schedule_id}/availability",
            json={"days": "[0]", "start_time": "09:00", "end_time": "17:00"},
        )

        et_resp = await client.post(
            "/api/v1/event-types",
            json={
                "title": "BufferTest",
                "slug": "buffer-test",
                "length": 30,
                "slot_interval": 30,
                "minimum_booking_notice": 0,
                "before_event_buffer": 30,
                "after_event_buffer": 30,
                "schedule_id": schedule_id,
            },
            headers=headers,
        )
        assert et_resp.status_code == 201

        booking_start = datetime.combine(NEXT_MONDAY, time(11, 0), tzinfo=ZoneInfo("Europe/London"))
        await client.post(
            "/api/v1/demo/buffer-test/bookings",
            json={
                "start": booking_start.isoformat(),
                "attendee": {
                    "name": "John",
                    "email": "john@example.com",
                    "time_zone": "Europe/London",
                },
            },
        )

        response = await client.get(
            f"/api/v1/demo/buffer-test/slots?date={NEXT_MONDAY.isoformat()}&timezone=Europe/London"
        )
        assert response.status_code == 200
        data = response.json()
        slot_times = [datetime.fromisoformat(s["time"]).astimezone(ZoneInfo("Europe/London")) for s in data["slots"]]

        # Booking 11:00-11:30, before_buffer=30, after_buffer=30
        # Blocked range: 10:30-12:00 → slots 10:30, 11:00, 11:30 excluded
        # 16 total − 3 = 13
        assert len(data["slots"]) == 13

        excluded = {(10, 30), (11, 0), (11, 30)}
        for st in slot_times:
            assert (st.hour, st.minute) not in excluded
