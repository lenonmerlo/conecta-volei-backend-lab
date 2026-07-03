from uuid import uuid4

from app.domain.constants import PlayerStatus
from app.modules.players.repository import PlayerRepository
from app.modules.players.schemas import PlayerCreate, PlayerRead, PlayerUpdate


def list_players(repository: PlayerRepository) -> list[PlayerRead]:
    return repository.list()

def get_player(repository: PlayerRepository, player_id: str) -> PlayerRead | None:
    return repository.get(player_id)

def get_player_by_whatsapp(
        repository: PlayerRepository,
        whatsapp: str,
) -> PlayerRead | None:
    normalized_whatsapp = whatsapp.strip()
    return repository.get_by_whatsapp(normalized_whatsapp)


def create_player(
        repository: PlayerRepository,
        payload: PlayerCreate,
) -> PlayerRead:
    existing_player = get_player_by_whatsapp(repository, payload.whatsapp)
    if existing_player:
        raise ValueError("Este WhatsApp já está cadastrado.")

    player = PlayerRead(
        id=str(uuid4()),
        name=payload.name.strip(),
        nickname=payload.nickname.strip() if payload.nickname else None,
        whatsapp=payload.whatsapp.strip(),
        gender=payload.gender,
        type=payload.type,
        status=PlayerStatus.PENDING,
        warnings=0,
    )

    return repository.create(player)

def update_player(
        repository: PlayerRepository,
        player_id: str,
        payload: PlayerUpdate,
) -> PlayerRead | None:
    current_player = get_player(repository, player_id)
    if current_player is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    next_whatsapp = update_data.get("whatsapp")
    if next_whatsapp is not None:
        existing_player = get_player_by_whatsapp(repository, next_whatsapp)
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

    return repository.update(updated_player)


def delete_player(repository: PlayerRepository, player_id: str) -> bool:
    return repository.delete(player_id)

