from datetime import UTC, datetime
from uuid import uuid4

from app.domain.constants import MAX_PLAYERS, PlayerStatus
from app.modules.games.service import get_game
from app.modules.players.repository import PlayerRepository
from app.modules.players.service import get_player
from app.modules.registrations.schemas import (
    RegistrationJoin,
    RegistrationLeave,
    RegistrationRead,
    RegistrationSlot,
)

_registrations: dict[str, RegistrationRead] = {}


def list_registrations(game_id: str) -> list[RegistrationRead]:
    return sorted(
        [
            registration
            for registration in _registrations.values()
            if registration.game_id == game_id
        ],
        key=lambda registration: registration.registered_at,
    )


def get_registration(registration_id: str) -> RegistrationRead | None:
    return _registrations.get(registration_id)


def _get_player_registration(
    game_id: str,
    player_id: str,
) -> RegistrationRead | None:
    for registration in _registrations.values():
        if registration.game_id == game_id and registration.player_id == player_id:
            return registration

    return None


def _main_count(game_id: str) -> int:
    return sum(
        1
        for registration in _registrations.values()
        if (
            registration.game_id == game_id
            and registration.slot == RegistrationSlot.MAIN
        )
    )


def _next_slot(game_id: str, player_status: PlayerStatus) -> RegistrationSlot:
    if player_status == PlayerStatus.PENALIZED:
        return RegistrationSlot.WAITLIST

    if _main_count(game_id) < MAX_PLAYERS:
        return RegistrationSlot.MAIN

    return RegistrationSlot.WAITLIST


def join_game(
    payload: RegistrationJoin,
    player_repository: PlayerRepository,
) -> RegistrationRead:
    game = get_game(payload.game_id)
    if game is None:
        raise ValueError("Game not found.")

    player = get_player(player_repository, payload.player_id)
    if player is None:
        raise ValueError("Player not found.")

    if player.status == PlayerStatus.BLOCKED:
        raise PermissionError("Blocked players cannot join games.")

    existing_registration = _get_player_registration(
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
        slot=_next_slot(payload.game_id, player.status),
        registered_at=datetime.now(UTC),
    )

    _registrations[registration.id] = registration
    return registration


def leave_game(payload: RegistrationLeave) -> bool:
    registration = _get_player_registration(payload.game_id, payload.player_id)
    if registration is None:
        return False

    removed_from_main = registration.slot == RegistrationSlot.MAIN
    del _registrations[registration.id]

    if removed_from_main:
        promote_from_waitlist(payload.game_id)

    return True


def promote_from_waitlist(game_id: str) -> RegistrationRead | None:
    if _main_count(game_id) >= MAX_PLAYERS:
        return None

    waitlist = [
        registration
        for registration in list_registrations(game_id)
        if registration.slot == RegistrationSlot.WAITLIST
    ]

    if not waitlist:
        return None

    first_waitlist = waitlist[0]
    promoted = first_waitlist.model_copy(update={"slot": RegistrationSlot.MAIN})
    _registrations[promoted.id] = promoted

    return promoted


def clear_registrations() -> None:
    _registrations.clear()