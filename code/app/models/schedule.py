from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    time_zone: Mapped[str] = mapped_column(String(64), default="Europe/London")

    owner = relationship("User", back_populates="schedules")
    availability = relationship("Availability", back_populates="schedule", cascade="all, delete-orphan")
    event_types = relationship("EventType", back_populates="schedule")

    def __repr__(self) -> str:
        return f"<Schedule {self.owner_id}/{self.name}>"
