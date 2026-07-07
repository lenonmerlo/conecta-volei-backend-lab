from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.domain.constants import PlayerStatus
from app.modules.auth.schemas import TokenResponse
from app.modules.players.repository import PlayerRepository
from app.modules.players.schemas import PlayerRead
from app.modules.players.service import get_player, get_player_by_whatsapp


def _build_token_response(player: PlayerRead) -> TokenResponse:
    access_token = create_access_token(
        subject=player.id,
        secret_key=settings.jwt_secret_key,
        expires_in_minutes=settings.jwt_access_token_expire_minutes,
    )
    refresh_token = create_refresh_token(
        subject=player.id,
        secret_key=settings.jwt_secret_key,
        expires_in_minutes=settings.jwt_refresh_token_expire_minutes,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        player=player,
    )


def login_by_whatsapp(
    repository: PlayerRepository,
    whatsapp: str,
) -> TokenResponse:
    player = get_player_by_whatsapp(repository, whatsapp)
    if player is None:
        raise ValueError("Invalid credentials.")

    if player.status == PlayerStatus.BLOCKED:
        raise PermissionError("Blocked players cannot login.")

    return _build_token_response(player)


def refresh_access_token(
    repository: PlayerRepository,
    refresh_token: str,
) -> TokenResponse:
    payload = decode_refresh_token(
        refresh_token,
        secret_key=settings.jwt_secret_key,
    )
    if payload is None:
        raise ValueError("Invalid refresh token.")

    player_id = payload.get("sub")
    if not isinstance(player_id, str):
        raise ValueError("Invalid refresh token.")

    player = get_current_player(repository, player_id)
    if player.status == PlayerStatus.BLOCKED:
        raise PermissionError("Blocked players cannot refresh token.")

    return _build_token_response(player)


def get_current_player(
    repository: PlayerRepository,
    player_id: str,
) -> PlayerRead:
    player = get_player(repository, player_id)
    if player is None:
        raise ValueError("Invalid credentials.")

    return player