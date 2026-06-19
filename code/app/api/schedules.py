from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.db import get_db
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import (
    AvailabilityCreate,
    AvailabilityResponse,
    ScheduleCreate,
    ScheduleResponse,
)

router = APIRouter(prefix="/api/v1/schedules", tags=["Schedules"])


@router.post("", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    body: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Schedule:
    schedule = Schedule(**body.model_dump(), owner_id=current_user.id)
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule, ["availability"])
    return schedule


@router.get("", response_model=list[ScheduleResponse])
async def list_schedules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Schedule]:
    result = await db.execute(
        select(Schedule)
        .where(Schedule.owner_id == current_user.id)
        .options(selectinload(Schedule.availability))
    )
    return list(result.scalars().all())


@router.post("/{schedule_id}/availability", response_model=AvailabilityResponse, status_code=201)
async def add_availability(
    schedule_id: int, body: AvailabilityCreate, db: AsyncSession = Depends(get_db)
) -> dict:
    from app.models.availability import Availability

    availability = Availability(schedule_id=schedule_id, **body.model_dump())
    db.add(availability)
    await db.commit()
    await db.refresh(availability)
    return availability
