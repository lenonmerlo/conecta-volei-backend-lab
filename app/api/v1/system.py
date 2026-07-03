from fastapi import APIRouter
from sqlalchemy import text

from app.core.cache import ping_cache
from app.core.database import SessionLocal

router = APIRouter(tags=["system"])

@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/ready")
def ready() -> dict[str, str]:
    with SessionLocal() as session:
        session.execute(text("SELECT 1"))

    ping_cache()

    return {
        "status": "ready",
        "database": "ok",
        "cache": "ok",
    }