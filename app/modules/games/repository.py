from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.games.model import GameModel
from app.modules.games.schemas import GameRead


class GameRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[GameRead]:
        games = self.db.scalars(
            select(GameModel).order_by(GameModel.date, GameModel.time),
        ).all()

        return [self._to_read_model(game) for game in games]

    def get(self, game_id: str) -> GameRead | None:
        game = self.db.get(GameModel, game_id)
        if game is None:
            return None

        return self._to_read_model(game)

    def create(self, game: GameRead) -> GameRead:
        model = GameModel(
            id=game.id,
            day=game.day.value,
            date=game.date,
            location=game.location,
            time=game.time,
            status=game.status,
            notes=game.notes,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._to_read_model(model)

    def update(self, game: GameRead) -> GameRead | None:
        model = self.db.get(GameModel, game.id)
        if model is None:
            return None

        model.day = game.day.value
        model.date = game.date
        model.location = game.location
        model.time = game.time
        model.status = game.status
        model.notes = game.notes

        self.db.commit()
        self.db.refresh(model)

        return self._to_read_model(model)

    def replace_id(self, old_game_id: str, game: GameRead) -> GameRead | None:
        old_model = self.db.get(GameModel, old_game_id)
        if old_model is None:
            return None

        self.db.delete(old_model)
        self.db.flush()

        model = GameModel(
            id=game.id,
            day=game.day.value,
            date=game.date,
            location=game.location,
            time=game.time,
            status=game.status,
            notes=game.notes,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._to_read_model(model)

    def delete(self, game_id: str) -> bool:
        model = self.db.get(GameModel, game_id)
        if model is None:
            return False

        self.db.delete(model)
        self.db.commit()

        return True

    @staticmethod
    def _to_read_model(game: GameModel) -> GameRead:
        return GameRead(
            id=game.id,
            day=game.day,
            date=game.date,
            location=game.location,
            time=game.time,
            status=game.status,
            notes=game.notes,
        )
