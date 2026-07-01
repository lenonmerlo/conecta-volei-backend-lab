from fastapi import APIRouter, HTTPException, status

from app.modules.players import service
from app.modules.players.schemas import PlayerCreate, PlayerRead, PlayerUpdate

router = APIRouter(prefix="/players", tags=["players"])

@router.get("", response_model=list[PlayerRead])
def list_players() -> list[PlayerRead]:
    return service.list_players()

@router.get("/{player_id}", response_model=PlayerRead)
def get_player(player_id: str) -> PlayerRead:
    player = service.get_player(player_id)
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found."
        )

    return player

@router.post("", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
def create_player(payload: PlayerCreate) -> PlayerRead:
    try:
        return service.create_player(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

@router.patch("/{player_id}", response_model=PlayerRead)
def update_player(player_id: str, payload: PlayerUpdate) -> PlayerRead:
    try:
        player = service.update_player(player_id, payload)
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
def delete_player(player_id: str) -> None:
    deleted = service.delete_player(player_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found.",
        )