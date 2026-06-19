from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.schedule import Schedule
from app.schemas.schedule import AvailabilityCreate, AvailabilityResponse, ScheduleCreate, ScheduleResponse

router = APIRouter(prefix="/api/v1/schedules", tags=["Schedules"])


@router.post("", response_model=ScheduleResponse, status_code=201)
async def create_schedule(body: ScheduleCreate, db: AsyncSession = Depends(get_db)) -> Schedule:
    schedule = Schedule(**body.model_dump(), owner_id=1)  # TODO: get from auth
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule, ["availability"])
    return schedule


@router.get("", response_model=list[ScheduleResponse])
async def list_schedules(db: AsyncSession = Depends(get_db)) -> list[Schedule]:
    result = await db.execute(
        select(Schedule).where(Schedule.owner_id == 1).options(selectinload(Schedule.availability))
    )  # TODO: auth
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
