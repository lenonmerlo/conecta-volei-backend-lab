import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def create_test_player(client: TestClient):
    def _create_test_player(
        whatsapp: str,
        *,
        status: str = "active",
        name: str = "Player Test",
        player_type: str = "member",
    ) -> dict:
        response = client.post(
            "/api/v1/players",
            json={
                "name": name,
                "nickname": None,
                "whatsapp": whatsapp,
                "gender": "M",
                "type": player_type,
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


@pytest.fixture(autouse=True)
def disable_registration_joined_event(monkeypatch):
    def fake_publish_registration_joined_event(**event) -> None:
        return None

    monkeypatch.setattr(
        "app.modules.registrations.service.publish_registration_joined_event",
        fake_publish_registration_joined_event,
    )

@pytest.fixture
def auth_headers(client: TestClient):
    def _auth_headers(whatsapp: str) -> dict[str, str]:
        response = client.post(
            "/api/v1/auth/login",
            json={"whatsapp": whatsapp},
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers


@pytest.fixture
def create_test_admin(client: TestClient, auth_headers):
    def _create_test_admin(
        whatsapp: str = "27990000999",
    ) -> dict:
        response = client.post(
            "/api/v1/players",
            json={
                "name": "Admin Test",
                "nickname": None,
                "whatsapp": whatsapp,
                "gender": "M",
                "type": "member",
            },
        )
        admin = response.json()

        client.patch(
            f"/api/v1/players/{admin['id']}",
            json={
                "status": "active",
                "role": "admin",
            },
        )

        admin["headers"] = auth_headers(whatsapp)
        return admin

    return _create_test_admin

def assert_error_response(
    response,
    *,
    status_code: int,
    message: str,
    code: str = "http_error",
) -> None:
    assert response.status_code == status_code
    assert response.json() == {
        "error": {
            "code": code,
            "message": message,
        },
    }