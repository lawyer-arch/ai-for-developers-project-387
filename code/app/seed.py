"""Идемпотентный seed-скрипт: создаёт демонстрационного пользователя, расписание и тип встречи."""

import asyncio
import json
import logging
from datetime import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Base, async_session, engine
from app.models.user import User
from app.models.schedule import Schedule
from app.models.availability import Availability
from app.models.event_type import EventType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

SEED_USER = {
    "username": "demo",
    "email": "demo@example.com",
    "name": "Demo User",
    "time_zone": "Europe/Moscow",
}

SEED_SCHEDULE = {
    "name": "Working hours",
    "time_zone": "Europe/Moscow",
}

SEED_AVAILABILITY = {
    "days": json.dumps([0, 1, 2, 3, 4]),
    "start_time": time(9, 0),
    "end_time": time(17, 0),
}

SEED_EVENT_TYPE = {
    "title": "Consultation",
    "slug": "consult",
    "description": "30-minute consultation meeting",
    "length": 30,
    "slot_interval": 15,
    "minimum_booking_notice": 120,
    "before_event_buffer": 0,
    "after_event_buffer": 0,
    "requires_confirmation": False,
    "location": "Zoom",
}


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # 1. User
        result = await session.execute(select(User).where(User.username == SEED_USER["username"]))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(**SEED_USER)
            session.add(user)
            await session.flush()
            log.info("Created user: %s (id=%d)", user.username, user.id)
        else:
            log.info("User already exists: %s (id=%d)", user.username, user.id)

        # 2. Schedule
        result = await session.execute(
            select(Schedule).where(Schedule.owner_id == user.id, Schedule.name == SEED_SCHEDULE["name"])
        )
        schedule = result.scalar_one_or_none()
        if schedule is None:
            schedule = Schedule(owner_id=user.id, **SEED_SCHEDULE)
            session.add(schedule)
            await session.flush()
            log.info("Created schedule: %s (id=%d)", schedule.name, schedule.id)
        else:
            log.info("Schedule already exists: %s (id=%d)", schedule.name, schedule.id)

        # 3. Availability
        result = await session.execute(
            select(Availability).where(
                Availability.schedule_id == schedule.id,
                Availability.days == SEED_AVAILABILITY["days"],
            )
        )
        avail = result.scalar_one_or_none()
        if avail is None:
            avail = Availability(schedule_id=schedule.id, **SEED_AVAILABILITY)
            session.add(avail)
            await session.flush()
            log.info("Created availability: %s", avail.days)
        else:
            log.info("Availability already exists: %s", avail.days)

        # 4. EventType
        result = await session.execute(
            select(EventType).where(EventType.owner_id == user.id, EventType.slug == SEED_EVENT_TYPE["slug"])
        )
        event_type = result.scalar_one_or_none()
        if event_type is None:
            event_type = EventType(owner_id=user.id, schedule_id=schedule.id, **SEED_EVENT_TYPE)
            session.add(event_type)
            await session.flush()
            log.info("Created event type: %s/%s (id=%d)", user.username, event_type.slug, event_type.id)
        else:
            log.info("Event type already exists: %s/%s (id=%d)", user.username, event_type.slug, event_type.id)

        await session.commit()
    log.info("Seed completed.")


if __name__ == "__main__":
    asyncio.run(seed())
