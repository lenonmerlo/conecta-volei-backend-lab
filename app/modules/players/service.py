from uuid import uuid4

from app.domain.constants import PlayerStatus, PlayerType
from app.modules.players.schemas import PlayerCreate, PlayerRead, PlayerUpdate

_players: dict[str, PlayerRead] = {}

def list_players() -> list[PlayerRead]:
    return sorted(_players.values(), key=lambda player: player.name.lower())

def get_player(player_id: str) -> PlayerRead | None:
    return _players.get(player_id)

def get_player_by_whatsapp(whatsapp: str) -> PlayerRead | None:
    normalized_whatsapp = whatsapp.strip()

    for player in _players.values():
        if player.whatsapp == normalized_whatsapp:
            return player

    return None

def create_player(payload: PlayerCreate) -> PlayerRead:
    existing_player = get_player_by_whatsapp(payload.whatsapp)
    if existing_player:
        raise ValueError("Este WhatsApp já está cadastrado.")

    player = PlayerRead(
        id=str(uuid4()),
        name=payload.name.strip(),
        nickname=payload.nickname.strip() if payload.nickname else None,
        whatsapp=payload.whatsapp.strip(),
        gender=payload.gender,
        type=PlayerType.MEMBER,
        status=PlayerStatus.PENDING,
        warnings=0,
    )

    _players[player.id] = player
    return player

def update_player(player_id: str, payload: PlayerUpdate) -> PlayerRead | None:
    current_player = get_player(player_id)
    if current_player is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    next_whatsapp = update_data.get("whatsapp")
    if next_whatsapp is not None:
        existing_player = get_player_by_whatsapp(next_whatsapp)
        if existing_player and existing_player.id != player_id:
            raise ValueError("Este WhatsApp já está cadastrado.")

    updated_player = current_player.model_copy(
        update={
            **update_data,
            "name": update_data.get("name", current_player.name).strip(),
            "nickname": (
                update_data["nickname"].strip()
                if update_data.get("nickname")
                else update_data.get("nickname", current_player.nickname)
            ),
            "whatsapp": update_data.get(
                "whatsapp",
                current_player.whatsapp,
            ).strip(),
        },
    )

    _players[player_id] = updated_player
    return updated_player

def delete_player(player_id: str) -> bool:
    return _players.pop(player_id, None) is not None

def clear_players() -> None:
    _players.clear()