from fastapi import APIRouter, HTTPException, status

from app.modules.games import service
from app.modules.games.schemas import GameCreate, GameRead, GameUpdate

router = APIRouter(prefix="/games", tags=["games"])

@router.get("", response_model=list[GameRead])
def list_games() -> list[GameRead]:
    return service.list_games()

@router.get("/{game_id}", response_model=GameRead)
def get_game(game_id: str) -> GameRead:
    game = service.get_game(game_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )

    return game

@router.post("", response_model=GameRead, status_code=status.HTTP_201_CREATED)
def create_game(payload: GameCreate) -> GameRead:
    try:
        return service.create_game(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

@router.patch("/{game_id}", response_model=GameRead)
def update_game(game_id: str, payload: GameUpdate) -> GameRead:
    try:
        game = service.update_game(game_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )

    return game

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: str) -> None:
    deleted = service.delete_game(game_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )



