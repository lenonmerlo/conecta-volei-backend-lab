from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.games.repository import GameRepository
from app.modules.players.repository import PlayerRepository
from app.modules.registrations import service
from app.modules.registrations.repository import RegistrationRepository
from app.modules.registrations.schemas import (
    RegistrationJoin,
    RegistrationLeave,
    RegistrationRead,
)

router = APIRouter(prefix="/registrations", tags=["registrations"])


def get_registration_repository(
    db: Annotated[Session, Depends(get_db_session)],
) -> RegistrationRepository:
    return RegistrationRepository(db)


def get_player_repository(
    db: Annotated[Session, Depends(get_db_session)],
) -> PlayerRepository:
    return PlayerRepository(db)


def get_game_repository(
    db: Annotated[Session, Depends(get_db_session)],
) -> GameRepository:
    return GameRepository(db)


@router.get("", response_model=list[RegistrationRead])
def list_registrations(
    registration_repository: Annotated[
        RegistrationRepository,
        Depends(get_registration_repository),
    ],
    game_id: str = Query(min_length=1),
) -> list[RegistrationRead]:
    return service.list_registrations(registration_repository, game_id)


@router.post(
    "/join",
    response_model=RegistrationRead,
    status_code=status.HTTP_201_CREATED,
)
def join_game(
    payload: RegistrationJoin,
    registration_repository: Annotated[
        RegistrationRepository,
        Depends(get_registration_repository),
    ],
    player_repository: Annotated[
        PlayerRepository,
        Depends(get_player_repository),
    ],
    game_repository: Annotated[
        GameRepository,
        Depends(get_game_repository),
    ],
) -> RegistrationRead:
    try:
        return service.join_game(
            payload,
            registration_repository,
            player_repository,
            game_repository,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        message = str(exc)
        error_status = (
            status.HTTP_404_NOT_FOUND
            if message in {"Game not found.", "Player not found."}
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(status_code=error_status, detail=message) from exc


@router.post("/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_game(
    payload: RegistrationLeave,
    registration_repository: Annotated[
        RegistrationRepository,
        Depends(get_registration_repository),
    ],
) -> None:
    removed = service.leave_game(payload, registration_repository)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found.",
        )