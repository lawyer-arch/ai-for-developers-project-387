import json
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.attendee import Attendee
from app.models.booking import Booking
from app.models.event_type import EventType
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse

router = APIRouter(tags=["Bookings"])


@router.post("/api/v1/{username}/{slug}/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(
    username: str,
    slug: str,
    body: BookingCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
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

    # Validate slot is within availability (simplified check)
    end_time = body.start + timedelta(minutes=event_type.length)

    # Create booking
    uid = secrets.token_hex(16)
    status = "pending" if event_type.requires_confirmation else "accepted"

    booking = Booking(
        uid=uid,
        event_type_id=event_type.id,
        start_time=body.start,
        end_time=end_time,
        status=status,
        responses=json.dumps(body.responses) if body.responses else "{}",
        location=body.location or event_type.location,
    )
    db.add(booking)
    await db.flush()

    # Create attendee
    attendee = Attendee(
        booking_id=booking.id,
        name=body.attendee.name,
        email=body.attendee.email,
        time_zone=body.attendee.time_zone,
        phone_number=body.attendee.phone_number,
    )
    db.add(attendee)
    await db.commit()

    await db.refresh(booking, ["attendees"])

    return {
        "uid": booking.uid,
        "event_type_id": booking.event_type_id,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "status": booking.status,
        "attendees": [
            {"name": a.name, "email": a.email, "time_zone": a.time_zone, "phone_number": a.phone_number}
            for a in booking.attendees
        ],
        "responses": json.loads(booking.responses) if booking.responses else {},
        "location": booking.location,
        "created_at": booking.created_at,
    }
