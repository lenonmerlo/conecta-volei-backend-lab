from datetime import UTC, datetime
from uuid import uuid4

from app.domain.constants import MAX_PLAYERS, PlayerStatus
from app.modules.games.repository import GameRepository
from app.modules.games.service import get_game
from app.modules.players.repository import PlayerRepository
from app.modules.players.service import get_player
from app.modules.registrations.repository import RegistrationRepository
from app.modules.registrations.schemas import (
    RegistrationJoin,
    RegistrationLeave,
    RegistrationRead,
    RegistrationSlot,
    RegistrationWithPlayerRead,
)


def list_registrations(
        repository: RegistrationRepository,
        game_id: str,
) -> list[RegistrationRead]:
   return repository.list_by_game(game_id)

def list_registrations_with_players(
    registration_repository: RegistrationRepository,
    game_id: str,
) -> list[RegistrationWithPlayerRead]:
    return registration_repository.list_with_players_by_game(game_id)

def _next_slot(
        repository: RegistrationRepository,
        game_id: str,
        player_status: PlayerStatus,
) -> RegistrationSlot:
    if player_status == PlayerStatus.PENALIZED:
        return RegistrationSlot.WAITLIST

    if repository.main_count(game_id) < MAX_PLAYERS:
        return RegistrationSlot.MAIN

    return RegistrationSlot.WAITLIST

def join_game(
        payload: RegistrationJoin,
        registration_repository: RegistrationRepository,
        player_repository: PlayerRepository,
        game_repository: GameRepository,
) -> RegistrationRead:
    game = get_game(game_repository, payload.game_id)
    if game is None:
        raise ValueError("Game not found.")

    player = get_player(player_repository, payload.player_id)
    if player is None:
        raise ValueError("Player not found.")

    if player.status == PlayerStatus.BLOCKED:
        raise PermissionError("Blocked players cannot join games.")

    existing_registration = registration_repository.get_player_registration(
        payload.game_id,
        payload.player_id,
    )
    if existing_registration:
        raise ValueError("Player already registered for this game.")

    registration = RegistrationRead(
        id=str(uuid4()),
        game_id=payload.game_id,
        player_id=payload.player_id,
        invited_by=payload.invited_by,
        slot=_next_slot(
            registration_repository,
            payload.game_id,
            player.status,
        ),
        registered_at=datetime.now(UTC),
    )

    return registration_repository.create(registration)

def leave_game(
        payload: RegistrationLeave,
        registration_repository: RegistrationRepository,
) -> bool:
    registration = registration_repository.get_player_registration(
        payload.game_id,
        payload.player_id,
    )
    if registration is None:
        return False

    removed_from_main = registration.slot == RegistrationSlot.MAIN
    deleted = registration_repository.delete(registration.id)

    if deleted and removed_from_main:
        promote_from_waitlist(payload.game_id, registration_repository)

    return deleted

def promote_from_waitlist(
        game_id: str,
        repository: RegistrationRepository,
) -> RegistrationRead | None:
    if repository.main_count(game_id) >= MAX_PLAYERS:
        return None

    first_waitlist = repository.first_waitlist(game_id)
    if first_waitlist is None:
        return None

    return repository.update_slot(first_waitlist.id, RegistrationSlot.MAIN)