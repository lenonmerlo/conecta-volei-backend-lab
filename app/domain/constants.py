from enum import StrEnum

MAX_PLAYERS = 21
PLAYERS_PER_TEAM = 7
TOTAL_TEAMS = 3

class GameDay(StrEnum):
    WEDNESDAY = "wednesday"
    SUNDAY = "sunday"

class PlayerStatus(StrEnum):
        ACTIVE = "active"
        PENDING = "pending"
        INACTIVE = "inactive"
        PENALIZED = "penalized"
        BLOCKED = "blocked"

class PlayerType(StrEnum):
    MEMBER = "member"
    GUEST = "guest"

SKILL_LEVELS = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]

