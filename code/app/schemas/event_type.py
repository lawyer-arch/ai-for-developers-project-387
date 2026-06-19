from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class EventTypeBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    description: str | None = Field(default=None, max_length=2048)
    length: int = Field(ge=1)
    slot_interval: int = Field(default=15, ge=1)
    minimum_booking_notice: int = Field(default=120, ge=0)
    before_event_buffer: int = Field(default=0, ge=0)
    after_event_buffer: int = Field(default=0, ge=0)
    requires_confirmation: bool = False
    location: str | None = Field(default=None, max_length=512)
    schedule_id: int | None = None


class EventTypeCreate(EventTypeBase):
    pass


class EventTypeResponse(EventTypeBase):
    id: int
    owner_id: int
    owner_username: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _extract_owner_username(cls, values: object) -> dict:
        if isinstance(values, dict):
            return values
        owner = getattr(values, "owner", None)
        username = getattr(owner, "username", "") if owner else ""
        attrs = {
            k: v
            for k, v in vars(values).items()
            if not k.startswith("_")
        }
        attrs["owner_username"] = username
        return attrs
