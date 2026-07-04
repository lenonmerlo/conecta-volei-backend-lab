from pydantic import BaseModel, Field

from app.domain.constants import PlayerRole, PlayerStatus, PlayerType


class PlayerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    nickname: str | None = Field(default=None, max_length=80)
    whatsapp: str = Field(min_length=8, max_length=20)
    gender: str = Field(min_length=1, max_length=1)
    type: PlayerType = PlayerType.MEMBER

class PlayerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    nickname: str | None = Field(default=None, max_length=80)
    whatsapp: str | None = Field(default=None, min_length=8, max_length=20)
    gender: str | None = Field(default=None, min_length=1, max_length=1)
    type: PlayerType | None = None
    role: PlayerRole | None = None
    status: PlayerStatus | None = None
    warnings: int | None = Field(default=None, ge=0)

class PlayerRead(BaseModel):
    id: str
    name: str
    nickname: str | None = None
    whatsapp: str
    gender: str
    type: PlayerType
    role: PlayerRole = PlayerRole.PLAYER
    status: PlayerStatus
    warnings: int = 0