from datetime import UTC, datetime
from uuid import uuid4

from app.modules.audit_logs.repository import AuditLogRepository
from app.modules.audit_logs.schemas import AuditLogCreate, AuditLogRead


def create_audit_log(
    repository: AuditLogRepository,
    payload: AuditLogCreate,
) -> AuditLogRead:
    audit_log = AuditLogRead(
        id=str(uuid4()),
        actor_player_id=payload.actor_player_id,
        target_player_id=payload.target_player_id,
        game_id=payload.game_id,
        action=payload.action,
        details=payload.details,
        created_at=datetime.now(UTC),
    )

    return repository.create(audit_log)

def list_audit_logs(repository: AuditLogRepository) -> list[AuditLogRead]:
    return repository.list()