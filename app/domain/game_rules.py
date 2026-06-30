from datetime import date, datetime, time, timedelta

from app.domain.constants import MAX_PLAYERS, GameDay, PlayerStatus, PlayerType


def has_spot_available(current_count: int) -> bool:
    return current_count < MAX_PLAYERS

def is_list_open(game_day: GameDay | str, now: datetime | None = None) -> bool:
    current = now or datetime.now()
    weekday = current.weekday()
    hour = current.hour

    if game_day == GameDay.WEDNESDAY:
        if weekday == 0 and hour >= 19:
            return True
        if weekday in {1, 2}:
            return True
        return False

    if game_day == GameDay.SUNDAY:
        if weekday == 3 and hour >= 19:
            return True
        if weekday in {4, 5, 6}:
            return True
        return False

    return False

def is_member_priority_window(current: datetime) -> bool:
    weekday = current.weekday()
    hour = current.hour
    minute = current.minute

    if weekday == 3 and hour >= 19:
        return True

    if weekday == 4:
        if hour < 23:
            return True
        if hour == 23 and minute < 59:
            return True

    return False

def is_guest_allowed_in_main_list(current: datetime) -> bool:
    return current.weekday() in {5, 6}

def get_sunday_priority(
        player_status: PlayerStatus | str,
        player_type: PlayerType | str,
        current: datetime,
) -> int:
    if player_status == PlayerStatus.PENALIZED:
        return 4

    if player_type == PlayerType.MEMBER:
        return 1 if is_member_priority_window(current) else 2

    if player_type == PlayerType.GUEST:
        return 2 if is_guest_allowed_in_main_list(current) else 3

    return 3

def can_join_list(player_status: PlayerStatus | str) -> bool:
    return player_status != PlayerStatus.BLOCKED

def get_next_game_date(game_day: GameDay | str, today: date | None = None) -> date:
    current = today or date.today()
    target_weekday = 2 if game_day == GameDay.WEDNESDAY else 6

    days_until_target = target_weekday - current.weekday()
    if days_until_target < 0:
        days_until_target += 7

    return current + timedelta(days=days_until_target)

def get_cycle_open_at(game_day: GameDay | str, game_date: date) -> datetime | None:
    if game_day == GameDay.WEDNESDAY:
        open_date = game_date - timedelta(days=2)
        return datetime.combine(open_date, time(hour=19))

    if game_day == GameDay.SUNDAY:
        open_date = game_date - timedelta(days=3)
        return datetime.combine(open_date, time(hour=19))

    return None

def is_registration_in_current_cycle(
        registered_at: datetime,
        game_day: GameDay | str,
        game_date: date,
) -> bool:
    open_at = get_cycle_open_at(game_day, game_date)
    if open_at is None:
        return True

    return registered_at >= open_at

def is_saturday_after_21h_for_sunday_game(
        game_day: GameDay | str,
        game_date: date,
        now: datetime | None = None,
) -> bool:
    if game_day != GameDay.SUNDAY:
        return False

    current = now or datetime.now()
    cutoff = datetime.combine(game_date - timedelta(days=1), time(hour=21))

    return current >= cutoff
