from app.modules.games.cache import (
    GAMES_LIST_CACHE_KEY,
    get_cached_games,
    invalidate_games_cache,
    set_cached_games,
)
from app.modules.games.schemas import GameRead


def test_games_cache_round_trip() -> None:
    invalidate_games_cache()

    game = GameRead(
        id="sunday-2026-07-05",
        day="sunday",
        date="2026-07-05",
        location="Arena Cache",
        time="08:00:00",
        status="open",
        notes=None,
    )

    set_cached_games([game])

    cached_games = get_cached_games()

    assert cached_games == [game]

    invalidate_games_cache()

    assert get_cached_games() is None


def test_games_cache_uses_expected_key() -> None:
    assert GAMES_LIST_CACHE_KEY == "games:list"