from dataclasses import dataclass, field
from random import shuffle


@dataclass(frozen=True)
class DrawPlayer:
    id: str
    name: str
    skill_level: float = 3
    gender: str | None = None
    is_captain: bool = False
    is_setter: bool = False
    position: str = "all-around"

@dataclass
class DrawTeam:
    name: str
    players: list[DrawPlayer] = field(default_factory=list)

    @property
    def total_level(self) -> float:
        return sum(float(player.skill_level or 0) for player in self.players)

def get_team_count(total_players: int) -> int:
    if total_players >= 14:
        return 3

    if total_players >= 8:
        return 2

    return 0

def draw_teams(players: list[DrawPlayer]) -> list[DrawTeam]:
    team_count = get_team_count(len(players))
    if team_count == 0:
        return []

    teams = [
        DrawTeam(name=f"Time {chr(65 + index)}")
        for index in range(team_count)
    ]
    max_per_team = (len(players) + team_count - 1) // team_count
    assigned_ids: set[str] = set()

    def can_add_to_team(team: DrawTeam) -> bool:
        return len(team.players) < max_per_team

    def try_add(team: DrawTeam, player: DrawPlayer | None) -> bool:
        if player is None:
            return False

        if player.id in assigned_ids:
            return False

        if not can_add_to_team(team):
            return False

        team.players.append(player)
        assigned_ids.add(player.id)
        return True

    def get_sorted_targets() -> list[DrawTeam]:
        return sorted(
            [team for team in teams if can_add_to_team(team)],
            key=lambda team: (
                len(team.players),
                team.total_level,
                sum(1 for player in team.players if player.gender == "F")
            ),
        )

    def assign_to_best_team(
            player: DrawPlayer,
            *,
            prefer_female_balance: bool = False,
    ) -> bool:
        targets = get_sorted_targets()
        if not targets:
            return False

        if prefer_female_balance:
            targets = sorted(
                targets,
                key=lambda team: (
                    len(team.players),
                    sum(1 for item in team.players if item.gender == "F")
                ),
            )

        return try_add(targets[0], player)

    captains = [player for player in players if player.is_captain]
    fixed_setters = [
        player
        for player in players
        if player.position == "setter" and not player.is_captain
    ]
    optional_setters = [
        player
        for player in players
        if player.is_setter and player.position != "setter" and not player.is_captain
    ]
    attackers = [
        player
        for player in players
        if (
            player.position == "attacker"
            and not player.is_captain
            and not player.is_setter
        )
    ]
    remaining = [
        player
        for player in players
        if (
            not player.is_captain
            and player.position != "setter"
            and not player.is_setter
            and player.position != "attacker"
        )
    ]

    for group in [captains, fixed_setters, optional_setters, attackers, remaining]:
        shuffle(group)

    for team_index in range(team_count):
        captain = captains.pop(0) if captains else None
        try_add(teams[team_index], captain)

    for player in captains:
        assign_to_best_team(player)

    for team_index in  range(team_count):
        setter = fixed_setters.pop(0) if fixed_setters else None
        if setter is None and optional_setters:
            setter = optional_setters.pop(0)

        try_add(teams[team_index], setter)

    for player in fixed_setters:
        assign_to_best_team(player)

    for player in optional_setters:
        assign_to_best_team(player)

    for player in attackers:
        assign_to_best_team(player)

    for player in remaining:
        assign_to_best_team(player, prefer_female_balance=player.gender == "FF")

    not_assigned = [player for player in players if player.id not in assigned_ids]
    for player in not_assigned:
        assign_to_best_team(player)

    return teams

def swap_players(
        teams: list[DrawTeam],
        from_team_index: int,
        from_player_id: str,
        to_team_index: int,
        to_player_id: str,
) -> list[DrawTeam]:
    if len(teams) < 2:
        return teams

    if from_team_index == to_team_index:
        return teams

    if from_team_index >= len(teams) or to_team_index >= len(teams):
        return teams

    new_teams = [
        DrawTeam(name=team.name, players=[*team.players])
        for team in teams
    ]

    from_team = new_teams[from_team_index]
    to_team = new_teams[to_team_index]

    from_index = next(
        (
            index
            for index, player in enumerate(from_team.players)
            if player.id == from_player_id
        ),
        None,
    )
    to_index = next(
        (
            index
            for index, player in enumerate(to_team.players)
            if player.id == to_player_id
        ),
        None,
    )

    if from_index is None or to_index is None:
        return teams

    from_team.players[from_index], to_team.players[to_index] = (
        to_team.players[to_index],
        from_team.players[from_index],
    )

    return new_teams




