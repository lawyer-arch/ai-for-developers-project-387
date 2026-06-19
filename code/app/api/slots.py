from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.availability import Availability
from app.models.booking import Booking
from app.models.event_type import EventType
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.slots import Slot, SlotsResponse

router = APIRouter(tags=["Slots"])


async def get_available_slots(
    event_type: EventType,
    target_date: date,
    booker_tz: str,
    db: AsyncSession,
) -> list[Slot]:
    host_tz = ZoneInfo(event_type.schedule.time_zone if event_type.schedule else "Europe/London")
    booker_timezone = ZoneInfo(booker_tz)

    # 1. Find schedule
    schedule = event_type.schedule
    if not schedule:
        return []

    # 2. Get availability windows for the target weekday
    weekday = target_date.weekday()  # 0=mon..6=sun
    result = await db.execute(
        select(Availability).where(
            Availability.schedule_id == schedule.id,
            Availability.days.contains(str(weekday)),
        )
    )
    windows = result.scalars().all()

    # 3. Generate candidate slots
    slot_duration = timedelta(minutes=event_type.length)
    interval = timedelta(minutes=event_type.slot_interval)
    now = datetime.now(host_tz)
    min_notice = timedelta(minutes=event_type.minimum_booking_notice)
    min_bookable = now + min_notice

    candidates = []
    for window in windows:
        slot_start = datetime.combine(
            target_date,
            window.start_time,
            tzinfo=host_tz,
        )
        slot_end = datetime.combine(
            target_date,
            window.end_time,
            tzinfo=host_tz,
        )
        current = slot_start
        while current + slot_duration <= slot_end:
            if current >= min_bookable:
                candidates.append(current)
            current += interval

    # 4. Get booked ranges with buffers
    day_start = datetime.combine(target_date, time.min, tzinfo=host_tz)
    day_end = datetime.combine(target_date, time.max, tzinfo=host_tz)
    result = await db.execute(
        select(Booking).where(
            Booking.event_type_id == event_type.id,
            Booking.status.in_(["accepted", "pending"]),
            Booking.start_time < day_end,
            Booking.end_time > day_start,
        )
    )
    bookings = result.scalars().all()
    booked_ranges = []
    for b in bookings:
        bs = b.start_time.replace(tzinfo=host_tz) if b.start_time.tzinfo is None else b.start_time
        be = b.end_time.replace(tzinfo=host_tz) if b.end_time.tzinfo is None else b.end_time
        booked_ranges.append((
            bs - timedelta(minutes=event_type.before_event_buffer),
            be + timedelta(minutes=event_type.after_event_buffer),
        ))

    # 5. Filter out occupied slots
    available = []
    for slot in candidates:
        slot_end_time = slot + slot_duration
        occupied = any(
            slot < booked_end and slot_end_time > booked_start
            for booked_start, booked_end in booked_ranges
        )
        if not occupied:
            slot_in_booker_tz = slot.astimezone(booker_timezone)
            available.append(Slot(time=slot_in_booker_tz, available=True))

    return available


@router.get("/api/v1/{username}/{slug}/slots", response_model=SlotsResponse)
async def get_slots(
    username: str,
    slug: str,
    date_str: str = Query(..., alias="date", description="Date in YYYY-MM-DD format"),
    timezone: str = Query(default="Europe/Moscow"),
    db: AsyncSession = Depends(get_db),
) -> SlotsResponse:
    # Find user
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find event type
    result = await db.execute(
        select(EventType).where(
            EventType.owner_id == user.id,
            EventType.slug == slug,
        )
    )
    event_type = result.scalar_one_or_none()
    if not event_type:
        raise HTTPException(status_code=404, detail="Event type not found")

    # Load schedule
    if event_type.schedule_id:
        result = await db.execute(select(Schedule).where(Schedule.id == event_type.schedule_id))
        event_type.schedule = result.scalar_one_or_none()

    # Parse date
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format. Use YYYY-MM-DD")

    # Get available slots
    slots = await get_available_slots(event_type, target_date, timezone, db)

    return SlotsResponse(date=date_str, timezone=timezone, slots=slots)
