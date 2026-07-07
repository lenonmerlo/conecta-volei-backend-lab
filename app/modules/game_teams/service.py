from datetime import UTC, datetime
from uuid import uuid4

from app.modules.game_teams.model import GameTeamModel
from app.modules.game_teams.repository import GameTeamRepository
from app.modules.game_teams.schemas import GameTeamRead, SaveGameTeamsPayload
from app.modules.games.repository import GameRepository


def list_game_teams(
        game_repository: GameRepository,
        team_repository: GameTeamRepository,
        game_id: str,
) -> list[GameTeamRead]:
    game = game_repository.get(game_id)
    if game is None:
        raise ValueError("Game not found.")

    return team_repository.list_by_game(game_id)

def save_game_teams(
        game_repository: GameRepository,
        team_repository: GameTeamRepository,
        game_id: str,
        payload: SaveGameTeamsPayload,
) -> list[GameTeamRead]:
    game = game_repository.get(game_id)
    if game is None:
        raise ValueError("Game not found.")

    teams = [
        GameTeamModel(
            id=str(uuid4()),
            game_id=game_id,
            team_name=team.name,
            players=team.players,
            total_level=team.total_level,
            created_at=datetime.now(UTC)
        )
        for team in payload.teams
    ]

    return team_repository.replace_for_game(game_id, teams)