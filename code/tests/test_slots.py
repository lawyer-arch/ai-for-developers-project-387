from datetime import datetime as dt
from typing import Any
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from httpx import AsyncClient


def _freeze_slots_datetime(frozen_dt: dt) -> Any:
    """Patch app.api.slots.datetime so that datetime.now() returns frozen_dt."""

    class _FrozenDatetime(dt):
        @classmethod
        def now(cls, tz=None):  # type: ignore[no-untyped-def]
            return frozen_dt.astimezone(tz) if tz else frozen_dt

    return patch("app.api.slots.datetime", _FrozenDatetime)


@pytest.mark.asyncio
async def test_slots_minimum_booking_notice(client: AsyncClient, auth_token: str) -> None:
    """Slots before now + minimum_booking_notice (default 120 min) should be excluded."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create schedule with all-days availability
    resp = await client.post(
        "/api/v1/schedules",
        json={"name": "Full Week", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    sched_id = resp.json()["id"]

    await client.post(
        f"/api/v1/schedules/{sched_id}/availability",
        json={
            "days": "[0,1,2,3,4,5,6]",
            "start_time": "09:00",
            "end_time": "17:00",
        },
    )

    await client.post(
        "/api/v1/event-types",
        json={
            "title": "Short Notice",
            "slug": "short-notice",
            "length": 30,
            "slot_interval": 30,
            "schedule_id": sched_id,
            "minimum_booking_notice": 120,
        },
        headers=headers,
    )

    # Freeze at 2026-06-22 (Monday) 09:00 MSK
    # min_bookable = 09:00 + 120min = 11:00
    frozen = dt(2026, 6, 22, 9, 0, 0, tzinfo=ZoneInfo("Europe/Moscow"))

    with _freeze_slots_datetime(frozen):
        resp = await client.get(
            "/api/v1/demo/short-notice/slots",
            params={"date": "2026-06-22", "timezone": "Europe/Moscow"},
        )

    assert resp.status_code == 200
    data = resp.json()
    slots = data["slots"]

    assert len(slots) > 0, "Should return some slots"

    min_bookable = dt(2026, 6, 22, 11, 0, 0, tzinfo=ZoneInfo("Europe/Moscow"))

    for s in slots:
        t = dt.fromisoformat(s["time"])
        assert t >= min_bookable, f"Slot {t} is before minimum bookable time"
        assert s["available"] is True

    # Earliest should be 11:00
    earliest = min(dt.fromisoformat(s["time"]) for s in slots)
    assert earliest == min_bookable


@pytest.mark.asyncio
async def test_slots_minimum_booking_notice_zero(client: AsyncClient, auth_token: str) -> None:
    """With minimum_booking_notice = 0, all availability slots should be returned."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    resp = await client.post(
        "/api/v1/schedules",
        json={"name": "Zero Notice", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    sched_id = resp.json()["id"]

    await client.post(
        f"/api/v1/schedules/{sched_id}/availability",
        json={
            "days": "[0]",
            "start_time": "10:00",
            "end_time": "12:00",
        },
    )

    await client.post(
        "/api/v1/event-types",
        json={
            "title": "Zero Notice",
            "slug": "zero-notice",
            "length": 30,
            "slot_interval": 30,
            "schedule_id": sched_id,
            "minimum_booking_notice": 0,
        },
        headers=headers,
    )

    frozen = dt(2026, 6, 22, 10, 0, 0, tzinfo=ZoneInfo("Europe/Moscow"))

    with _freeze_slots_datetime(frozen):
        resp = await client.get(
            "/api/v1/demo/zero-notice/slots",
            params={"date": "2026-06-22", "timezone": "Europe/Moscow"},
        )

    assert resp.status_code == 200
    slots = resp.json()["slots"]

    # 10:00-12:00 with 30min slots: 10:00, 10:30, 11:00, 11:30 = 4 slots
    assert len(slots) == 4
    for s in slots:
        assert s["available"] is True


@pytest.mark.asyncio
async def test_slots_with_buffers(client: AsyncClient, auth_token: str) -> None:
    """Slots within before/after_event_buffer of a booking should be unavailable."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    resp = await client.post(
        "/api/v1/schedules",
        json={"name": "Buffer Test", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    sched_id = resp.json()["id"]

    await client.post(
        f"/api/v1/schedules/{sched_id}/availability",
        json={
            "days": "[0]",
            "start_time": "09:00",
            "end_time": "17:00",
        },
    )

    await client.post(
        "/api/v1/event-types",
        json={
            "title": "Buffer Test",
            "slug": "buffer-test",
            "length": 30,
            "slot_interval": 30,
            "schedule_id": sched_id,
            "minimum_booking_notice": 0,
            "before_event_buffer": 30,
            "after_event_buffer": 30,
        },
        headers=headers,
    )

    # Create a booking at 12:00-12:30 on Monday 2026-06-22
    await client.post(
        "/api/v1/demo/buffer-test/bookings",
        json={
            "start": "2026-06-22T12:00:00+03:00",
            "attendee": {
                "name": "Guest",
                "email": "guest@example.com",
                "time_zone": "Europe/Moscow",
            },
        },
    )

    frozen = dt(2026, 6, 22, 0, 0, 0, tzinfo=ZoneInfo("Europe/Moscow"))

    with _freeze_slots_datetime(frozen):
        resp = await client.get(
            "/api/v1/demo/buffer-test/slots",
            params={"date": "2026-06-22", "timezone": "Europe/Moscow"},
        )

    assert resp.status_code == 200
    slots = resp.json()["slots"]

    slot_map = {}
    for s in slots:
        t = dt.fromisoformat(s["time"])
        slot_map[t] = s["available"]

    # Booking 12:00-12:30 with 30min buffers → protected range 11:30-13:00
    expected_unavailable = {
        dt(2026, 6, 22, 11, 30, tzinfo=ZoneInfo("Europe/Moscow")),
        dt(2026, 6, 22, 12, 0, 0, tzinfo=ZoneInfo("Europe/Moscow")),
        dt(2026, 6, 22, 12, 30, tzinfo=ZoneInfo("Europe/Moscow")),
    }

    for slot_time, available in slot_map.items():
        if slot_time in expected_unavailable:
            assert available is False, f"Slot {slot_time} should be unavailable (buffer)"
        else:
            assert available is True, f"Slot {slot_time} should be available"


@pytest.mark.asyncio
async def test_slots_with_buffers_zero(client: AsyncClient, auth_token: str) -> None:
    """With zero buffers, only the exact booking slot should be unavailable."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    resp = await client.post(
        "/api/v1/schedules",
        json={"name": "No Buffer", "time_zone": "Europe/Moscow"},
        headers=headers,
    )
    sched_id = resp.json()["id"]

    await client.post(
        f"/api/v1/schedules/{sched_id}/availability",
        json={
            "days": "[0]",
            "start_time": "09:00",
            "end_time": "17:00",
        },
    )

    await client.post(
        "/api/v1/event-types",
        json={
            "title": "No Buffer",
            "slug": "no-buffer",
            "length": 30,
            "slot_interval": 30,
            "schedule_id": sched_id,
            "minimum_booking_notice": 0,
            "before_event_buffer": 0,
            "after_event_buffer": 0,
        },
        headers=headers,
    )

    await client.post(
        "/api/v1/demo/no-buffer/bookings",
        json={
            "start": "2026-06-22T12:00:00+03:00",
            "attendee": {
                "name": "Guest",
                "email": "guest@example.com",
                "time_zone": "Europe/Moscow",
            },
        },
    )

    frozen = dt(2026, 6, 22, 0, 0, 0, tzinfo=ZoneInfo("Europe/Moscow"))

    with _freeze_slots_datetime(frozen):
        resp = await client.get(
            "/api/v1/demo/no-buffer/slots",
            params={"date": "2026-06-22", "timezone": "Europe/Moscow"},
        )

    assert resp.status_code == 200
    slots = resp.json()["slots"]

    for s in slots:
        t = dt.fromisoformat(s["time"])
        if t == dt(2026, 6, 22, 12, 0, tzinfo=ZoneInfo("Europe/Moscow")):
            assert s["available"] is False, "Exact booking slot should be unavailable"
        else:
            assert s["available"] is True, f"Slot {t} should be available"
