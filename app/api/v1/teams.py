from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.auth import require_admin
from app.modules.players.schemas import PlayerRead
from app.modules.teams import service
from app.modules.teams.schemas import DrawTeamRead, DrawTeamsPayload, SwapTeamsPayload

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("")
def list_teams() -> list[dict[str, str]]:
    return []


@router.post("/draw", response_model=list[DrawTeamRead])
def draw_team_groups(
    payload: DrawTeamsPayload,
    _admin: Annotated[PlayerRead, Depends(require_admin)],
) -> list[DrawTeamRead]:
    return service.draw_team_groups(payload)


@router.post("/swap", response_model=list[DrawTeamRead])
def swap_team_players(
    payload: SwapTeamsPayload,
    _admin: Annotated[PlayerRead, Depends(require_admin)],
) -> list[DrawTeamRead]:
    return service.swap_team_players(payload)