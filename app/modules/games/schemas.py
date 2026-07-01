from datetime import date as Date
from datetime import time as Time

from pydantic import BaseModel, Field

from app.domain.constants import GameDay


class GameCreate(BaseModel):
    date: Date
    location: str = Field(min_length=2, max_length=160)
    time: Time
    status: str = Field(default="active", min_length=2, max_length=40)
    notes: str | None = Field(default=None, max_length=500)


class GameUpdate(BaseModel):
    date: Date | None = None
    location: str | None = Field(default=None, min_length=2, max_length=160)
    time: Time | None = None
    status: str | None = Field(default=None, min_length=2, max_length=40)
    notes: str | None = Field(default=None, max_length=500)


class GameRead(BaseModel):
    id: str
    day: GameDay
    date: Date
    location: str
    time: Time
    status: str
    notes: str | None = None