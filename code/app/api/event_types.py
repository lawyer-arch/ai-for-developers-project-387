from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth import get_current_user
from app.db import get_db
from app.models.event_type import EventType
from app.models.user import User
from app.schemas.event_type import EventTypeCreate, EventTypeResponse, EventTypeUpdate

router = APIRouter(prefix="/api/v1/event-types", tags=["Event Types"])


@router.post("", response_model=EventTypeResponse, status_code=201)
async def create_event_type(
    body: EventTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EventType:
    event_type = EventType(**body.model_dump(), owner_id=current_user.id)
    db.add(event_type)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An event type with this slug already exists",
        )
    result = await db.execute(
        select(EventType).options(joinedload(EventType.owner)).where(EventType.id == event_type.id)
    )
    return result.scalar_one()


@router.get("", response_model=list[EventTypeResponse])
async def list_event_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EventType]:
    result = await db.execute(
        select(EventType)
        .options(joinedload(EventType.owner))
        .where(EventType.owner_id == current_user.id)
    )
    return list(result.scalars().all())


@router.get("/{event_type_id}", response_model=EventTypeResponse)
async def get_event_type(event_type_id: int, db: AsyncSession = Depends(get_db)) -> EventType:
    result = await db.execute(
        select(EventType).options(joinedload(EventType.owner)).where(EventType.id == event_type_id)
    )
    event_type = result.scalar_one_or_none()
    if not event_type:
        raise HTTPException(status_code=404, detail="Event type not found")
    return event_type


@router.patch("/{event_type_id}", response_model=EventTypeResponse)
async def update_event_type(
    event_type_id: int,
    body: EventTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EventType:
    result = await db.execute(
        select(EventType).options(joinedload(EventType.owner)).where(EventType.id == event_type_id)
    )
    event_type = result.scalar_one_or_none()
    if not event_type:
        raise HTTPException(status_code=404, detail="Event type not found")
    if event_type.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this event type")

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for field, value in update_data.items():
        setattr(event_type, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An event type with this slug already exists",
        )
    await db.refresh(event_type)
    return event_type


@router.delete("/{event_type_id}", status_code=204)
async def delete_event_type(
    event_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(
        select(EventType).where(EventType.id == event_type_id)
    )
    event_type = result.scalar_one_or_none()
    if not event_type:
        raise HTTPException(status_code=404, detail="Event type not found")
    if event_type.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this event type")

    await db.delete(event_type)
    await db.commit()
