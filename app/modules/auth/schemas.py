from pydantic import BaseModel, Field

from app.modules.players.schemas import PlayerRead


class LoginRequest(BaseModel):
    whatsapp: str = Field(min_length=8, max_length=20)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    player: PlayerRead

    