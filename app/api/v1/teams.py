from fastapi import APIRouter

router = APIRouter(prefix="/teams", tags=["teams"])

@router.get("")
def list_teams() -> list[dict[str, str]]:
    return []