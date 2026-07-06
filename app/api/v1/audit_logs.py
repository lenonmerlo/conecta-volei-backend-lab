from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import require_admin
from app.core.database import get_db_session
from app.modules.audit_logs.repository import AuditLogRepository
from app.modules.audit_logs.schemas import AuditLogRead
from app.modules.audit_logs.service import list_audit_logs
from app.modules.players.schemas import PlayerRead

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])

DatabaseSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=list[AuditLogRead])
def list_logs(
    db: DatabaseSession,
    _admin: Annotated[PlayerRead, Depends(require_admin)],
) -> list[AuditLogRead]:
    repository = AuditLogRepository(db)
    return list_audit_logs(repository)