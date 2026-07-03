from app.core.cache import delete_key, get_json, set_json
from app.modules.games.schemas import GameRead

GAMES_LIST_CACHE_KEY = "games:list"
GAMES_LIST_CACHE_TTL_SECONDS = 60

def get_cached_games() -> list[GameRead] | None:
    cached_games = get_json(GAMES_LIST_CACHE_KEY)
    if cached_games is None:
        return None

    return [GameRead(**game) for game in cached_games]

def set_cached_games(games: list[GameRead]) -> None:
    set_json(
        GAMES_LIST_CACHE_KEY,
        [game.model_dump(mode="json") for game in games],
        ttl_seconds=GAMES_LIST_CACHE_TTL_SECONDS,
    )

def invalidate_games_cache() -> None:
    delete_key(GAMES_LIST_CACHE_KEY)
