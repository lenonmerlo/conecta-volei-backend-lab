from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GameTeamPayload(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    players: list[dict[str, Any]] = Field(min_length=1)
    total_level: float = Field(ge=0)

class SaveGameTeamsPayload(BaseModel):
    teams: list[GameTeamPayload] = Field(min_length=1)

class GameTeamRead(BaseModel):
    id: str
    game_id: str
    name: str
    players: list[dict[str, Any]]
    total_level: float
    created_at: datetime