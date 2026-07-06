from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.audit_logs.model import AuditLogModel
from app.modules.audit_logs.schemas import AuditLogRead


class AuditLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, audit_log: AuditLogRead) -> AuditLogRead:
        model = AuditLogModel(
            id=audit_log.id,
            actor_player_id=audit_log.actor_player_id,
            target_player_id=audit_log.target_player_id,
            game_id=audit_log.game_id,
            action=audit_log.action,
            details=audit_log.details,
            created_at=audit_log.created_at,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._to_read_model(model)

    def list(self) -> list[AuditLogRead]:
        audit_logs = self.db.scalars(
            select(AuditLogModel).order_by(AuditLogModel.created_at.desc()),
        ).all()

        return [self._to_read_model(audit_log) for audit_log in audit_logs]

    @staticmethod
    def _to_read_model(audit_log: AuditLogModel) -> AuditLogRead:
        return AuditLogRead(
            id=audit_log.id,
            actor_player_id=audit_log.actor_player_id,
            target_player_id=audit_log.target_player_id,
            game_id=audit_log.game_id,
            action=audit_log.action,
            details=audit_log.details,
            created_at=audit_log.created_at,
        )