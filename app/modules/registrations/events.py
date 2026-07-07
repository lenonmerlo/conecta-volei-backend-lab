import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

def handle_registration_event(body: bytes) -> dict[str, Any]:
    payload = json.loads(body.decode())

    event = payload.get("event")
    registration_id = payload.get("registration_id")
    game_id = payload.get("game_id")
    player_id = payload.get("player_id")
    slot = payload.get("slot")

    logger.info(
        "registration event consumed",
        extra={
            "event": event,
            "registration_id": registration_id,
            "game_id": game_id,
            "player_id": player_id,
            "slot": slot,
        },
    )

    return payload