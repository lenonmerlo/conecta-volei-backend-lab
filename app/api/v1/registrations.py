from fastapi import APIRouter

router = APIRouter(prefix="/registrations", tags=["registrations"])

@router.get("")
def list_registrations() -> list[dict[str, str]]:
    return []
