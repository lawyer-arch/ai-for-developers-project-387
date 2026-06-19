from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Attendee(Base):
    __tablename__ = "attendees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(254), index=True)
    time_zone: Mapped[str] = mapped_column(String(64), default="Europe/London")
    phone_number: Mapped[str | None] = mapped_column(String(32), default=None)

    booking = relationship("Booking", back_populates="attendees")

    def __repr__(self) -> str:
        return f"<Attendee {self.name} <{self.email}>>"
