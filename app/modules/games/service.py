from datetime import date

from app.domain.constants import GameDay
from app.modules.games.cache import (
    get_cached_games,
    invalidate_games_cache,
    set_cached_games,
)
from app.modules.games.repository import GameRepository
from app.modules.games.schemas import GameCreate, GameRead, GameUpdate


def _get_game_day(game_date: date) -> GameDay:
    if game_date.weekday() == 2:
        return GameDay.WEDNESDAY

    if game_date.weekday() == 6:
        return GameDay.SUNDAY

    raise ValueError("Games must be scheduled on Wednesday or Sunday.")


def _build_game_id(game_day: GameDay, game_date: date) -> str:
    return f"{game_day.value}-{game_date.isoformat()}"


def list_games(repository: GameRepository) -> list[GameRead]:
    cached_games = get_cached_games()
    if cached_games is not None:
        return cached_games

    games = repository.list()
    set_cached_games(games)

    return games

def get_game(repository: GameRepository, game_id: str) -> GameRead | None:
    return repository.get(game_id)


def create_game(repository: GameRepository, payload: GameCreate) -> GameRead:
    game_day = _get_game_day(payload.date)
    game_id = _build_game_id(game_day, payload.date)

    if repository.get(game_id):
        raise ValueError("Este jogo já está cadastrado.")

    game = GameRead(
        id=game_id,
        day=game_day,
        date=payload.date,
        location=payload.location.strip(),
        time=payload.time,
        status=payload.status,
        notes=payload.notes.strip() if payload.notes else None,
    )

    created_game = repository.create(game)
    invalidate_games_cache()
    return created_game


def update_game(
        repository: GameRepository,
        game_id: str,
        payload: GameUpdate,
) -> GameRead | None:
    current_game = get_game(repository, game_id)
    if current_game is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    next_date = update_data.get("date", current_game.date)
    next_day = _get_game_day(next_date)
    next_id = _build_game_id(next_day, next_date)

    if next_id != game_id and repository.get(next_id):
        raise ValueError("Este jogo já está cadastrado.")

    updated_game = current_game.model_copy(
        update={
            **update_data,
            "id": next_id,
            "day": next_day,
            "location": update_data.get(
                "location",
                current_game.location,
            ).strip(),
            "status": update_data.get("status", current_game.status).strip(),
            "notes": (
                update_data["notes"].strip()
                if update_data.get("notes")
                else update_data.get("notes", current_game.notes)
            ),
        },
    )

    if next_id != game_id:
        return repository.replace_id(game_id, updated_game)

    updated_game = repository.update(updated_game)
    invalidate_games_cache()
    return updated_game


def delete_game(repository: GameRepository, game_id: str) -> bool:
    deleted = repository.delete(game_id)
    if deleted:
        invalidate_games_cache()

    return deleted
