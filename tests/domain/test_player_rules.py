from app.domain.constants import PlayerStatus
from app.domain.player_rules import status_from_warnings


def test_status_from_zero_warnings_is_active() -> None:
    assert status_from_warnings(0) == PlayerStatus.ACTIVE


def test_status_from_two_warnings_is_penalized() -> None:
    assert status_from_warnings(2) == PlayerStatus.PENALIZED


def test_status_from_three_warnings_is_blocked() -> None:
    assert status_from_warnings(3) == PlayerStatus.BLOCKED