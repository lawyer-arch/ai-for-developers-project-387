from fastapi import FastAPI

from app.api import bookings, event_types, schedules, slots
from app.db import Base, engine

app = FastAPI(title="Scheduling Service API", version="1.0.0")

app.include_router(event_types.router)
app.include_router(schedules.router)
app.include_router(slots.router)
app.include_router(bookings.router)


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
