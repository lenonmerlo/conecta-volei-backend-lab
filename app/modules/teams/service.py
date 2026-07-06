from app.domain.team_draw import DrawPlayer, draw_teams
from app.modules.teams.schemas import (
    DrawPlayerRead,
    DrawTeamRead,
    DrawTeamsPayload,
)


def draw_team_groups(payload: DrawTeamsPayload) -> list[DrawTeamRead]:
    players = [
        DrawPlayer(
            id=player.id,
            name=player.name,
            skill_level=player.skill_level,
            gender=player.gender,
            is_captain=player.is_captain,
            is_setter=player.is_setter,
            position=player.position,
        )
        for player in payload.players
    ]

    teams = draw_teams(players)

    return [
        DrawTeamRead(
            name=team.name,
            total_level=team.total_level,
            players=[
                DrawPlayerRead(
                    id=player.id,
                    name=player.name,
                    skill_level=player.skill_level,
                    gender=player.gender,
                    is_captain=player.is_captain,
                    is_setter=player.is_setter,
                    position=player.position,
                )
                for player in team.players
            ],
        )
        for team in teams
    ]