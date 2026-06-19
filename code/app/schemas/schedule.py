from datetime import time

from pydantic import BaseModel, Field, model_validator


class AvailabilityResponse(BaseModel):
    id: int
    days: str
    start_time: str
    end_time: str
    specific_date: str | None = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _convert_times(cls, values: object) -> dict:
        if isinstance(values, dict):
            return values
        attrs = {k: v for k, v in vars(values).items() if not k.startswith("_")}
        for field in ("start_time", "end_time"):
            val = attrs.get(field)
            if isinstance(val, time):
                attrs[field] = val.strftime("%H:%M")
        return attrs


class ScheduleBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    time_zone: str = "Europe/Moscow"


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleResponse(ScheduleBase):
    id: int
    owner_id: int
    availability: list[AvailabilityResponse] = []

    model_config = {"from_attributes": True}


class AvailabilityCreate(BaseModel):
    days: str  # JSON array stored as string: "[0,1,2,3,4]"
    start_time: str  # "HH:MM"
    end_time: str  # "HH:MM"
    specific_date: str | None = None
