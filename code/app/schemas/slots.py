from datetime import datetime

from pydantic import BaseModel


class Slot(BaseModel):
    time: datetime
    available: bool = True


class SlotsResponse(BaseModel):
    date: str
    timezone: str
    slots: list[Slot]
