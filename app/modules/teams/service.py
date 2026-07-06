from app.domain.team_draw import DrawPlayer, DrawTeam, draw_teams, swap_players
from app.modules.teams.schemas import (
    DrawPlayerPayload,
    DrawPlayerRead,
    DrawTeamRead,
    DrawTeamsPayload,
    SwapTeamsPayload,
)


def _to_draw_player(player: DrawPlayerPayload) -> DrawPlayer:
    return DrawPlayer(
        id=player.id,
        name=player.name,
        skill_level=player.skill_level,
        gender=player.gender,
        is_captain=player.is_captain,
        is_setter=player.is_setter,
        position=player.position,
    )

def _to_draw_player_read(player: DrawPlayer) -> DrawPlayerRead:
    return DrawPlayerRead(
        id=player.id,
        name=player.name,
        skill_level=player.skill_level,
        gender=player.gender,
        is_captain=player.is_captain,
        is_setter=player.is_setter,
        position=player.position
    )

def _to_draw_team_read(team: DrawTeam) -> DrawTeamRead:
    return DrawTeamRead(
        name=team.name,
        total_level=team.total_level,
        players=[_to_draw_player_read(player) for player in team.players],
    )

def draw_team_groups(payload: DrawTeamsPayload) -> list[DrawTeamRead]:
    players = [_to_draw_player(player) for player in payload.players]
    teams = draw_teams(players)

    return [_to_draw_team_read(team) for team in teams]

def swap_team_players(payload: SwapTeamsPayload) -> list[DrawTeamRead]:
    teams = [
        DrawTeam(
            name=team.name,
            players=[_to_draw_player(player) for player in team.players],
        )
        for team in payload.teams
    ]

    swapped_teams = swap_players(
        teams,
        payload.from_team_index,
        payload.from_player_id,
        payload.to_team_index,
        payload.to_player_id,
    )

    return [_to_draw_team_read(team) for team in swapped_teams]