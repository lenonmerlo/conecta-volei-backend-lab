from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditLogCreate(BaseModel):
    actor_player_id: str | None = None
    target_player_id: str | None = None
    game_id: str | None = None
    action: str = Field(min_length=1, max_length=80)
    details: dict[str, Any] | None = None

class AuditLogRead(BaseModel):
    id: str
    actor_player_id: str | None = None
    target_player_id: str | None = None
    game_id: str | None = None
    action: str
    details: dict[str, Any] | None = None
    created_at: datetime

