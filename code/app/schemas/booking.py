from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class AttendeeBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    time_zone: str = "Europe/London"
    phone_number: str | None = Field(default=None, max_length=32)


class AttendeeCreate(AttendeeBase):
    pass


class AttendeeResponse(AttendeeBase):
    model_config = {"from_attributes": True}


class BookingCreate(BaseModel):
    start: datetime
    attendee: AttendeeCreate
    responses: dict | None = None
    location: str | None = None


class BookingResponse(BaseModel):
    uid: str
    event_type_id: int | None
    start_time: datetime
    end_time: datetime
    status: str
    attendees: list[AttendeeResponse] = []
    responses: dict = {}
    location: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
