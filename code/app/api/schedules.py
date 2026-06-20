from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.db import get_db
from app.models.availability import Availability
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import (
    AvailabilityCreate,
    AvailabilityResponse,
    AvailabilityUpdate,
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
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


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Schedule:
    result = await db.execute(
        select(Schedule)
        .where(Schedule.id == schedule_id)
        .options(selectinload(Schedule.availability))
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if schedule.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this schedule")
    return schedule


@router.patch("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    body: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Schedule:
    result = await db.execute(
        select(Schedule)
        .where(Schedule.id == schedule_id)
        .options(selectinload(Schedule.availability))
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if schedule.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this schedule")

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for field, value in update_data.items():
        setattr(schedule, field, value)

    await db.commit()
    await db.refresh(schedule, ["availability"])
    return schedule


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if schedule.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this schedule")

    await db.delete(schedule)
    await db.commit()


@router.post("/{schedule_id}/availability", response_model=AvailabilityResponse, status_code=201)
async def add_availability(
    schedule_id: int, body: AvailabilityCreate, db: AsyncSession = Depends(get_db)
) -> Availability:
    availability = Availability(schedule_id=schedule_id, **body.model_dump())
    db.add(availability)
    await db.commit()
    await db.refresh(availability)
    return availability


@router.patch(
    "/{schedule_id}/availability/{availability_id}",
    response_model=AvailabilityResponse,
)
async def update_availability(
    schedule_id: int,
    availability_id: int,
    body: AvailabilityUpdate,
    db: AsyncSession = Depends(get_db),
) -> Availability:
    result = await db.execute(
        select(Availability).where(
            Availability.id == availability_id,
            Availability.schedule_id == schedule_id,
        )
    )
    availability = result.scalar_one_or_none()
    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for field, value in update_data.items():
        setattr(availability, field, value)

    await db.commit()
    await db.refresh(availability)
    return availability


@router.delete(
    "/{schedule_id}/availability/{availability_id}",
    status_code=204,
)
async def delete_availability(
    schedule_id: int,
    availability_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Availability).where(
            Availability.id == availability_id,
            Availability.schedule_id == schedule_id,
        )
    )
    availability = result.scalar_one_or_none()
    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")

    await db.delete(availability)
    await db.commit()
