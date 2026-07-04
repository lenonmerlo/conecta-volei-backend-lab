from app.core.config import settings
from app.core.security import create_access_token
from app.domain.constants import PlayerStatus
from app.modules.auth.schemas import TokenResponse
from app.modules.players.repository import PlayerRepository
from app.modules.players.service import get_player, get_player_by_whatsapp


def login_by_whatsapp(
        repository: PlayerRepository,
        whatsapp: str,
) -> TokenResponse:
    player = get_player_by_whatsapp(repository, whatsapp)
    if player is None:
        raise ValueError("Invalid credentials.")

    if player.status == PlayerStatus.BLOCKED:
        raise PermissionError("Blocked players cannot login.")

    access_token = create_access_token(
        subject=player.id,
        secret_key=settings.jwt_secret_key,
        expires_in_minutes=settings.jwt_access_token_expire_minutes,
    )

    return TokenResponse(
        access_token=access_token,
        player=player,
    )

def get_current_player(
        repository: PlayerRepository,
        player_id: str,
):
    player = get_player(repository, player_id)
    if player is None:
        raise ValueError("Invalid credentials.")

    return player