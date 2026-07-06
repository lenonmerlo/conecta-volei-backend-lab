from fastapi import APIRouter

from app.api.v1 import audit_logs, auth, games, players, registrations, system, teams

router = APIRouter(prefix="/v1")

router.include_router(system.router)
router.include_router(players.router)
router.include_router(games.router)
router.include_router(registrations.router)
router.include_router(teams.router)
router.include_router(auth.router)
router.include_router(audit_logs.router)