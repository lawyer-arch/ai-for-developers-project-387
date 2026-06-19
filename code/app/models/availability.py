from sqlalchemy import Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Availability(Base):
    __tablename__ = "availability"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), index=True)
    days: Mapped[str] = mapped_column(String(20))  # JSON array stored as string: "[0,1,2,3,4]"
    start_time: Mapped[str] = mapped_column(Time)  # "HH:MM:SS"
    end_time: Mapped[str] = mapped_column(Time)    # "HH:MM:SS"
    specific_date: Mapped[str | None] = mapped_column(Date, default=None)

    schedule = relationship("Schedule", back_populates="availability")

    def __repr__(self) -> str:
        return f"<Availability {self.schedule_id} [{self.days}] {self.start_time}-{self.end_time}>"
