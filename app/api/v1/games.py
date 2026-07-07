from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.auth import require_admin
from app.core.database import get_db_session
from app.modules.game_teams.repository import GameTeamRepository
from app.modules.game_teams.schemas import GameTeamRead, SaveGameTeamsPayload
from app.modules.game_teams.service import list_game_teams, save_game_teams
from app.modules.games import service
from app.modules.games.repository import GameRepository
from app.modules.games.schemas import GameCreate, GameRead, GameUpdate
from app.modules.players.schemas import PlayerRead

router = APIRouter(prefix="/games", tags=["games"])

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_game_repository(db: DatabaseSession) -> GameRepository:
    return GameRepository(db)


def get_game_team_repository(db: DatabaseSession) -> GameTeamRepository:
    return GameTeamRepository(db)

@router.get("", response_model=list[GameRead])
def list_games(
        repository: Annotated[GameRepository, Depends(get_game_repository)],
) -> list[GameRead]:
    return service.list_games(repository)


@router.get("/{game_id}", response_model=GameRead)
def get_game(
        game_id: str,
        repository: Annotated[GameRepository, Depends(get_game_repository)],
) -> GameRead:
    game = service.get_game(repository, game_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )

    return game

@router.post("", response_model=GameRead, status_code=status.HTTP_201_CREATED)
def create_game(
        payload: GameCreate,
        repository: Annotated[GameRepository, Depends(get_game_repository)],
        _admin: Annotated[PlayerRead, Depends(require_admin)],
) -> GameRead:
    try:
        return service.create_game(repository, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

@router.patch("/{game_id}", response_model=GameRead)
def update_game(
        game_id: str,
        payload: GameUpdate,
        repository: Annotated[GameRepository, Depends(get_game_repository)],
        _admin: Annotated[PlayerRead, Depends(require_admin)],
) -> GameRead:
    try:
        game = service.update_game(repository, game_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )

    return game

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(
        game_id: str,
        repository: Annotated[GameRepository, Depends(get_game_repository)],
        _admin: Annotated[PlayerRead, Depends(require_admin)],
) -> None:
    deleted = service.delete_game(repository, game_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )

@router.get("/{game_id}/teams", response_model=list[GameTeamRead])
def get_game_teams(
    game_id: str,
    game_repository: Annotated[
        GameRepository,
        Depends(get_game_repository),
    ],
    team_repository: Annotated[
        GameTeamRepository,
        Depends(get_game_team_repository),
    ],
) -> list[GameTeamRead]:
    try:
        return list_game_teams(game_repository, team_repository, game_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put("/{game_id}/teams", response_model=list[GameTeamRead])
def put_game_teams(
    game_id: str,
    payload: SaveGameTeamsPayload,
    game_repository: Annotated[
        GameRepository,
        Depends(get_game_repository),
    ],
    team_repository: Annotated[
        GameTeamRepository,
        Depends(get_game_team_repository),
    ],
    _admin: Annotated[PlayerRead, Depends(require_admin)],
) -> list[GameTeamRead]:
    try:
        return save_game_teams(game_repository, team_repository, game_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

