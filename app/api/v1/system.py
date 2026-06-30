from fastapi import APIRouter

router = APIRouter(tags=["system"])

@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/ready")
def readiness_check() -> dict[str, str]:
    return {"status": "ready"}