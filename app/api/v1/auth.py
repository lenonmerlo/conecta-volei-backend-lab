from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db_session
from app.core.security import decode_access_token
from app.domain.constants import PlayerRole
from app.modules.auth import service
from app.modules.auth.schemas import LoginRequest, RefreshTokenRequest, TokenResponse
from app.modules.players.repository import PlayerRepository
from app.modules.players.schemas import PlayerRead

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_player_repository(db: DatabaseSession) -> PlayerRepository:
    return PlayerRepository(db)


def get_current_player(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
    repository: Annotated[
        PlayerRepository,
        Depends(get_player_repository),
    ],
) -> PlayerRead:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )

    token = credentials.credentials
    payload = decode_access_token(token, secret_key=settings.jwt_secret_key)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )

    player_id = payload.get("sub")
    if not isinstance(player_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )

    try:
        return service.get_current_player(repository, player_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


def require_admin(
        current_player: Annotated[PlayerRead, Depends(get_current_player)],
) -> PlayerRead:
    if current_player.role not in {
        PlayerRole.ADMIN,
        PlayerRole.SUPER_ADMIN,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required."
        )

    return current_player


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    repository: Annotated[
        PlayerRepository,
        Depends(get_player_repository),
    ],
) -> TokenResponse:
    try:
        return service.login_by_whatsapp(repository, payload.whatsapp)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshTokenRequest,
    repository: Annotated[
        PlayerRepository,
        Depends(get_player_repository),
    ],
) -> TokenResponse:
    try:
        return service.refresh_access_token(repository, payload.refresh_token)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.get("/me", response_model=PlayerRead)
def me(
    current_player: Annotated[PlayerRead, Depends(get_current_player)],
) -> PlayerRead:
    return current_player