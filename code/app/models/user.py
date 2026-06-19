from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), default=None)
    time_zone: Mapped[str] = mapped_column(String(64), default="Europe/London")

    event_types = relationship("EventType", back_populates="owner", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.username}>"
