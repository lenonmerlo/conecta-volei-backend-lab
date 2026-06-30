from datetime import date, datetime

from app.domain.constants import GameDay, PlayerStatus, PlayerType
from app.domain.game_rules import (
    can_join_list,
    get_next_game_date,
    get_sunday_priority,
    has_spot_available,
    is_guest_allowed_in_main_list,
    is_list_open,
    is_member_priority_window,
    is_registration_in_current_cycle,
    is_saturday_after_21h_for_sunday_game,
)


def test_has_spot_available_before_limit() -> None:
    assert has_spot_available(20) is True


def test_has_spot_available_at_limit() -> None:
    assert has_spot_available(21) is False


def test_wednesday_list_opens_on_monday_after_19h() -> None:
    monday_20h = datetime(2026, 5, 25, 20, 0)
    assert is_list_open(GameDay.WEDNESDAY, monday_20h) is True


def test_wednesday_list_is_closed_on_monday_before_19h() -> None:
    monday_18h = datetime(2026, 5, 25, 18, 0)
    assert is_list_open(GameDay.WEDNESDAY, monday_18h) is False


def test_sunday_list_opens_on_thursday_after_19h() -> None:
    thursday_20h = datetime(2026, 5, 28, 20, 0)
    assert is_list_open(GameDay.SUNDAY, thursday_20h) is True


def test_member_priority_window_on_thursday_after_19h() -> None:
    thursday_19h = datetime(2026, 5, 28, 19, 0)
    assert is_member_priority_window(thursday_19h) is True


def test_guest_allowed_in_main_list_on_saturday() -> None:
    saturday = datetime(2026, 5, 30, 10, 0)
    assert is_guest_allowed_in_main_list(saturday) is True


def test_penalized_player_has_lowest_sunday_priority() -> None:
    current = datetime(2026, 5, 28, 20, 0)

    assert (
        get_sunday_priority(PlayerStatus.PENALIZED, PlayerType.MEMBER, current)
        == 4
    )


def test_blocked_player_cannot_join_list() -> None:
    assert can_join_list(PlayerStatus.BLOCKED) is False


def test_active_player_can_join_list() -> None:
    assert can_join_list(PlayerStatus.ACTIVE) is True


def test_get_next_game_date_keeps_current_wednesday() -> None:
    current = date(2026, 6, 3)

    assert get_next_game_date(GameDay.WEDNESDAY, current) == date(2026, 6, 3)


def test_get_next_game_date_advances_after_wednesday() -> None:
    current = date(2026, 6, 4)

    assert get_next_game_date(GameDay.WEDNESDAY, current) == date(2026, 6, 10)


def test_registration_after_cycle_open_is_current() -> None:
    registered_at = datetime(2026, 5, 28, 19, 1)
    game_date = date(2026, 5, 31)

    assert (
        is_registration_in_current_cycle(
            registered_at,
            GameDay.SUNDAY,
            game_date,
        )
        is True
    )


def test_registration_before_cycle_open_is_not_current() -> None:
    registered_at = datetime(2026, 5, 28, 18, 59)
    game_date = date(2026, 5, 31)

    assert (
        is_registration_in_current_cycle(
            registered_at,
            GameDay.SUNDAY,
            game_date,
        )
        is False
    )


def test_saturday_after_21h_for_sunday_game_is_true() -> None:
    game_date = date(2026, 5, 31)
    saturday_21h = datetime(2026, 5, 30, 21, 0)

    assert (
        is_saturday_after_21h_for_sunday_game(
            GameDay.SUNDAY,
            game_date,
            saturday_21h,
        )
        is True
    )