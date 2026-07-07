import json

import pytest

from app.modules.registrations.events import handle_registration_event


def test_handle_registration_event_returns_payload() -> None:
    payload = {
        "event": "registration.joined",
        "registration_id": "registration-1",
        "game_id": "sunday-2026-07-05",
        "player_id": "player-1",
        "slot": "main",
    }

    result = handle_registration_event(json.dumps(payload).encode())

    assert result == payload


def test_handle_registration_event_raises_for_invalid_json() -> None:
    with pytest.raises(json.JSONDecodeError):
        handle_registration_event(b"invalid-json")