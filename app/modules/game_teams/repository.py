from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.game_teams.model import GameTeamModel
from app.modules.game_teams.schemas import GameTeamRead


class GameTeamRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_game(self, game_id: str) -> list[GameTeamRead]:
        statement = (
            select(GameTeamModel)
            .where(GameTeamModel.game_id == game_id)
            .order_by(GameTeamModel.team_name)
        )
        teams = self.db.execute(statement).scalars().all()
        
        return [self._to_read_model(team) for team in teams]

    def replace_for_game(
            self,
            game_id: str,
            teams: list[GameTeamRead]
    ) -> list[GameTeamRead]:
        self.db.execute(delete(GameTeamModel)
                        .where(GameTeamModel.game_id == game_id)
                        )

        for team in teams:
            self.db.add(team)

        self.db.commit()

        return self.list_by_game(game_id)

    def _to_read_model(self, team: GameTeamModel) -> GameTeamRead:
        return GameTeamRead(
            id=team.id,
            game_id=team.game_id,
            name=team.team_name,
            players=team.players,
            total_level=team.total_level,
            created_at=team.created_at,
        )

