from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.players.model import PlayerModel
from app.modules.players.schemas import PlayerRead


class PlayerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[PlayerRead]:
        players = self.db.scalars(
            select(PlayerModel).order_by(PlayerModel.name),
        ).all()

        return [self._to_read_model(player) for player in players]

    def get(self, player_id: str) -> PlayerRead | None:
        player = self.db.get(PlayerModel, player_id)
        if player is None:
            return None

        return self._to_read_model(player)

    def get_by_whatsapp(self, whatsapp: str) -> PlayerRead | None:
        player = self.db.scalar(
            select(PlayerModel).where(PlayerModel.whatsapp == whatsapp),
        )
        if player is None:
            return None

        return self._to_read_model(player)

    def create(self, player: PlayerRead) -> PlayerRead:
        model = PlayerModel(
            id=player.id,
            name=player.name,
            nickname=player.nickname,
            whatsapp=player.whatsapp,
            gender=player.gender,
            type=player.type.value,
            role=player.role.value,
            status=player.status.value,
            warnings=player.warnings,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._to_read_model(model)

    def update(self, player: PlayerRead) -> PlayerRead | None:
        model = self.db.get(PlayerModel, player.id)
        if model is None:
            return None

        model.name = player.name
        model.nickname = player.nickname
        model.whatsapp = player.whatsapp
        model.gender = player.gender
        model.type = player.type.value
        model.role = player.role.value
        model.status = player.status.value
        model.warnings = player.warnings

        self.db.commit()
        self.db.refresh(model)

        return self._to_read_model(model)

    def delete(self, player_id: str) -> bool:
        model = self.db.get(PlayerModel, player_id)
        if model is None:
            return False

        self.db.delete(model)
        self.db.commit()

        return True

    @staticmethod
    def _to_read_model(player: PlayerModel) -> PlayerRead:
        return PlayerRead(
            id=player.id,
            name=player.name,
            nickname=player.nickname,
            whatsapp=player.whatsapp,
            gender=player.gender,
            type=player.type,
            role=player.role,
            status=player.status,
            warnings=player.warnings
        )