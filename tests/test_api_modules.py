from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_players_module_is_registered() -> None:
    response = client.get("/api/v1/players")

    assert response.status_code == 200
    assert response.json() == []


def test_games_module_is_registered() -> None:
    response = client.get("/api/v1/games")

    assert response.status_code == 200
    assert response.json() == []


def test_registrations_module_is_registered() -> None:
    response = client.get("/api/v1/registrations")

    assert response.status_code == 200
    assert response.json() == []


def test_teams_module_is_registered() -> None:
    response = client.get("/api/v1/teams")

    assert response.status_code == 200
    assert response.json() == []