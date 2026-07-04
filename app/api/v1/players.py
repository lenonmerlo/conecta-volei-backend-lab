from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.auth import require_admin
from app.core.database import get_db_session
from app.modules.players import service
from app.modules.players.repository import PlayerRepository
from app.modules.players.schemas import PlayerCreate, PlayerRead, PlayerUpdate

DatabaseSession = Annotated[Session, Depends(get_db_session)]

router = APIRouter(prefix="/players", tags=["players"])

def get_player_repository(
    db: Annotated[Session, Depends(get_db_session)],
) -> PlayerRepository:
    return PlayerRepository(db)

@router.get("", response_model=list[PlayerRead])
def list_players(
        repository: Annotated[PlayerRepository, Depends(get_player_repository)],
) -> list[PlayerRead]:
    return service.list_players(repository)

@router.get("/{player_id}", response_model=PlayerRead)
def get_player(
        player_id: str,
        repository: Annotated[PlayerRepository, Depends(get_player_repository)],
) -> PlayerRead:
    player = service.get_player(repository, player_id)
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found.",
        )

    return player

@router.post("", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
def create_player(
        payload: PlayerCreate,
        repository: Annotated[PlayerRepository, Depends(get_player_repository)],
) -> PlayerRead:
    try:
        return service.create_player(repository, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

@router.post(
    "/{player_id}/warnings",
    response_model=PlayerRead,
)
def add_warning(
    player_id: str,
    db: DatabaseSession,
    admin: Annotated[PlayerRead, Depends(require_admin)],
) -> PlayerRead:
    repository = PlayerRepository(db)
    player = service.add_warning(repository, player_id)

    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found.",
        )

    return player

@router.delete(
    "/{player_id}/warnings",
    response_model=PlayerRead,
)
def remove_warning(
    player_id: str,
    db: DatabaseSession,
    admin: Annotated[PlayerRead, Depends(require_admin)],
) -> PlayerRead:
    repository = PlayerRepository(db)
    player = service.remove_warning(repository, player_id)

    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found.",
        )

    return player


@router.post(
    "/{player_id}/warnings/reset",
    response_model=PlayerRead,
)
def reset_warnings(
    player_id: str,
    db: DatabaseSession,
    admin: Annotated[PlayerRead, Depends(require_admin)],
) -> PlayerRead:
    repository = PlayerRepository(db)
    player = service.reset_warnings(repository, player_id)

    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found.",
        )

    return player

@router.patch("/{player_id}", response_model=PlayerRead)
def update_player(
        player_id: str,
        payload: PlayerUpdate,
        repository: Annotated[PlayerRepository, Depends(get_player_repository)],
) -> PlayerRead:
    try:
        player = service.update_player(repository, player_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found.",
        )

    return player

@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(
        player_id: str,
        repository: Annotated[PlayerRepository, Depends(get_player_repository)],
        _admin: Annotated[PlayerRead, Depends(require_admin)],
) -> None:
    deleted = service.delete_player(repository, player_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found.",
        )

