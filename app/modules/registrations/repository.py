from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.players.model import PlayerModel
from app.modules.registrations.model import RegistrationModel
from app.modules.registrations.schemas import (
    RegistrationRead,
    RegistrationSlot,
    RegistrationWithPlayerRead,
)


class RegistrationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_game(self, game_id: str) -> list[RegistrationRead]:
        registrations = self.db.scalars(
            select(RegistrationModel)
            .where(RegistrationModel.game_id == game_id)
            .order_by(RegistrationModel.registered_at),
        ).all()

        return [self._to_read_model(registration) for registration in registrations]

    def list_with_players_by_game(
        self,
        game_id: str,
    ) -> list[RegistrationWithPlayerRead]:
        statement = (
            select(RegistrationModel, PlayerModel)
            .join(PlayerModel, PlayerModel.id == RegistrationModel.player_id)
            .where(RegistrationModel.game_id == game_id)
            .order_by(RegistrationModel.registered_at)
        )

        rows = self.db.execute(statement).all()

        return [
            RegistrationWithPlayerRead(
                id=registration.id,
                game_id=registration.game_id,
                player_id=registration.player_id,
                player_name=player.name,
                player_nickname=player.nickname,
                invited_by=registration.invited_by,
                slot=registration.slot,
                registered_at=registration.registered_at,
            )
            for registration, player in rows
        ]

    def get_player_registration(
        self,
        game_id: str,
        player_id: str,
    ) -> RegistrationRead | None:
        registration = self.db.scalar(
            select(RegistrationModel).where(
                RegistrationModel.game_id == game_id,
                RegistrationModel.player_id == player_id,
            ),
        )
        if registration is None:
            return None

        return self._to_read_model(registration)

    def main_count(self, game_id: str) -> int:
        registrations = self.db.scalars(
            select(RegistrationModel).where(
                RegistrationModel.game_id == game_id,
                RegistrationModel.slot == RegistrationSlot.MAIN.value,
            ),
        ).all()

        return len(registrations)

    def first_waitlist(self, game_id: str) -> RegistrationRead | None:
        registration = self.db.scalar(
            select(RegistrationModel)
            .where(
                RegistrationModel.game_id == game_id,
                RegistrationModel.slot == RegistrationSlot.WAITLIST.value,
            )
            .order_by(RegistrationModel.registered_at),
        )
        if registration is None:
            return None

        return self._to_read_model(registration)

    def create(self, registration: RegistrationRead) -> RegistrationRead:
        model = RegistrationModel(
            id=registration.id,
            game_id=registration.game_id,
            player_id=registration.player_id,
            invited_by=registration.invited_by,
            slot=registration.slot.value,
            registered_at=registration.registered_at,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._to_read_model(model)

    def update_slot(
        self,
        registration_id: str,
        slot: RegistrationSlot,
    ) -> RegistrationRead | None:
        model = self.db.get(RegistrationModel, registration_id)
        if model is None:
            return None

        model.slot = slot.value

        self.db.commit()
        self.db.refresh(model)

        return self._to_read_model(model)

    def delete(self, registration_id: str) -> bool:
        model = self.db.get(RegistrationModel, registration_id)
        if model is None:
            return False

        self.db.delete(model)
        self.db.commit()

        return True

    @staticmethod
    def _to_read_model(registration: RegistrationModel) -> RegistrationRead:
        return RegistrationRead(
            id=registration.id,
            game_id=registration.game_id,
            player_id=registration.player_id,
            invited_by=registration.invited_by,
            slot=registration.slot,
            registered_at=registration.registered_at,
        )