from pydantic import BaseModel, Field


class DrawPlayerPayload(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    skill_level: float = 3
    gender: str | None = None
    is_captain: bool = False
    is_setter: bool = False
    position: str = "all-around"



class DrawTeamsPayload(BaseModel):
    players: list[DrawPlayerPayload] = Field(min_length=1)


class SwapTeamPayload(BaseModel):
    name: str = Field(min_length=1)
    players: list[DrawPlayerPayload] = Field(min_length=1)


class SwapTeamsPayload(BaseModel):
    teams: list[SwapTeamPayload] = Field(min_length=2)
    from_team_index: int = Field(ge=0)
    from_player_id: str = Field(min_length=1)
    to_team_index: int = Field(ge=0)
    to_player_id: str = Field(min_length=1)


class DrawPlayerRead(BaseModel):
    id: str
    name: str
    skill_level: float
    gender: str | None = None
    is_captain: bool
    is_setter: bool
    position: str


class DrawTeamRead(BaseModel):
    name: str
    total_level: float
    players: list[DrawPlayerRead]