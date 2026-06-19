from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    event_type_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("event_types.id", ondelete="SET NULL"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(16), default="accepted", index=True)
    responses: Mapped[str | None] = mapped_column(Text, default="{}")  # JSON stored as text for SQLite
    location: Mapped[str | None] = mapped_column(String(512), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    event_type = relationship("EventType", back_populates="bookings")
    attendees = relationship("Attendee", back_populates="booking", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Booking {self.uid}>"
