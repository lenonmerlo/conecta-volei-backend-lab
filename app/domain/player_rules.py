from app.domain.constants import PlayerStatus


def status_from_warnings(warnings: int) -> PlayerStatus:
    if warnings >= 3:
        return PlayerStatus.BLOCKED

    if warnings == 2:
        return PlayerStatus.PENALIZED

    return PlayerStatus.ACTIVE