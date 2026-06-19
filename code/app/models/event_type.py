from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class EventType(Base):
    __tablename__ = "event_types"
    __table_args__ = (
        UniqueConstraint("owner_id", "slug", name="uq_event_type_owner_slug"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(2048), default=None)
    length: Mapped[int] = mapped_column(Integer)
    slot_interval: Mapped[int] = mapped_column(Integer, default=15)
    minimum_booking_notice: Mapped[int] = mapped_column(Integer, default=120)
    before_event_buffer: Mapped[int] = mapped_column(Integer, default=0)
    after_event_buffer: Mapped[int] = mapped_column(Integer, default=0)
    requires_confirmation: Mapped[bool] = mapped_column(Boolean, default=False)
    location: Mapped[str | None] = mapped_column(String(512), default=None)
    schedule_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("schedules.id", ondelete="SET NULL"), default=None, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="event_types")
    schedule = relationship("Schedule", back_populates="event_types")
    bookings = relationship("Booking", back_populates="event_type", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<EventType {self.owner_id}/{self.slug}>"
