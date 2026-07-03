import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from app.main import app


@pytest.fixture
def client() -> TestClient:
    with SessionLocal() as session:
        session.execute(text("DELETE FROM game_registrations"))
        session.execute(text("DELETE FROM players"))
        session.execute(text("DELETE FROM games"))
        session.commit()

    return TestClient(app)


@pytest.fixture
def create_test_player(client: TestClient):
    def _create_test_player(
        whatsapp: str,
        *,
        status: str = "active",
        name: str = "Player Test",
    ) -> dict:
        response = client.post(
            "/api/v1/players",
            json={
                "name": name,
                "nickname": None,
                "whatsapp": whatsapp,
                "gender": "M",
            },
        )
        player = response.json()

        if status != "pending":
            update_response = client.patch(
                f"/api/v1/players/{player['id']}",
                json={"status": status},
            )
            return update_response.json()

        return player

    return _create_test_player


@pytest.fixture
def create_test_game(client: TestClient):
    def _create_test_game() -> dict:
        response = client.post(
            "/api/v1/games",
            json={
                "date": "2026-07-05",
                "location": "Arena Conecta",
                "time": "08:00:00",
            },
        )
        return response.json()

    return _create_test_game