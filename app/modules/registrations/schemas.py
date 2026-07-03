from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class RegistrationSlot(StrEnum):
    MAIN = "main"
    WAITLIST = "waitlist"
    GUESTS = "guests"

class RegistrationJoin(BaseModel):
    game_id: str
    player_id: str
    invited_by: str | None = None

class RegistrationLeave(BaseModel):
    game_id: str
    player_id: str

class RegistrationRead(BaseModel):
    id: str
    game_id: str
    player_id: str
    invited_by: str | None = None
    slot: RegistrationSlot
    registered_at: datetime

class RegistrationWithPlayerRead(RegistrationRead):
    player_name: str
    player_nickname: str | None = None

class RegistrationListQuery(BaseModel):
    game_id: str = Field(min_length=1)