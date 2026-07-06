from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.auth import require_admin
from app.core.database import get_db_session
from app.modules.audit_logs.repository import AuditLogRepository
from app.modules.audit_logs.schemas import AuditLogCreate
from app.modules.audit_logs.service import create_audit_log
from app.modules.games.repository import GameRepository
from app.modules.players.repository import PlayerRepository
from app.modules.players.schemas import PlayerRead
from app.modules.registrations import service
from app.modules.registrations.repository import RegistrationRepository
from app.modules.registrations.schemas import (
    RegistrationJoin,
    RegistrationLeave,
    RegistrationRead,
    RegistrationWithPlayerRead,
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

DatabaseSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=list[RegistrationWithPlayerRead])
def list_registrations(
    db: DatabaseSession,
    game_id: str = Query(min_length=1),
) -> list[RegistrationWithPlayerRead]:
    registration_repository = RegistrationRepository(db)
    return service.list_registrations_with_players(
        registration_repository,
        game_id,
    )

@router.post(
    "/join",
    response_model=RegistrationRead,
    status_code=status.HTTP_201_CREATED,
)
def join_game(
    payload: RegistrationJoin,
    db: DatabaseSession,
) -> RegistrationRead:
    registration_repository = RegistrationRepository(db)
    player_repository = PlayerRepository(db)
    game_repository = GameRepository(db)
    audit_log_repository = AuditLogRepository(db)

    try:
        registration = service.join_game(
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

    create_audit_log(
        audit_log_repository,
        AuditLogCreate(
            actor_player_id=payload.invited_by,
            target_player_id=payload.player_id,
            game_id=payload.game_id,
            action="registration.joined",
            details={
                "registration_id": registration.id,
                "slot": registration.slot,
                "invited_by": payload.invited_by,
            },
        ),
    )

    return registration


@router.post("/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_game(
    payload: RegistrationLeave,
    db: DatabaseSession,
) -> None:
    registration_repository = RegistrationRepository(db)
    audit_log_repository = AuditLogRepository(db)

    registration = registration_repository.get_player_registration(
        payload.game_id,
        payload.player_id,
    )
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found.",
        )

    removed = service.leave_game(payload, registration_repository)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found.",
        )

    create_audit_log(
        audit_log_repository,
        AuditLogCreate(
            actor_player_id=payload.player_id,
            target_player_id=payload.player_id,
            game_id=payload.game_id,
            action="registration.left",
            details={
                "registration_id": registration.id,
                "slot": registration.slot,
            },
        ),
    )

@router.post(
    "/process-guests",
    response_model=list[RegistrationRead],
)
def process_guest_registrations(
    db: DatabaseSession,
    admin: Annotated[PlayerRead, Depends(require_admin)],
    game_id: str = Query(min_length=1),
) -> list[RegistrationRead]:
    registration_repository = RegistrationRepository(db)
    audit_log_repository = AuditLogRepository(db)

    promoted_registrations = service.process_guest_registrations(
        game_id,
        registration_repository,
    )

    for registration in promoted_registrations:
        create_audit_log(
            audit_log_repository,
            AuditLogCreate(
                actor_player_id=admin.id,
                target_player_id=registration.player_id,
                game_id=registration.game_id,
                action="guest_registration.processed",
                details={
                    "registration_id": registration.id,
                    "new_slot": registration.slot,
                    "invited_by": registration.invited_by,
                },
            ),
        )

    return promoted_registrations