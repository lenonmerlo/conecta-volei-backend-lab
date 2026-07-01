from fastapi.testclient import TestClient

from app.main import app
from app.modules.games.service import clear_games
from app.modules.players.service import clear_players

client = TestClient(app)


def setup_function() -> None:
    clear_players()
    clear_games()


def test_players_module_is_registered() -> None:
    response = client.get("/api/v1/players")

    assert response.status_code == 200
    assert response.json() == []


def test_create_player_returns_created_player() -> None:
    response = client.post(
        "/api/v1/players",
        json={
            "name": "Lenon Merlo",
            "nickname": "Lenon",
            "whatsapp": "27997343401",
            "gender": "M",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"]
    assert data["name"] == "Lenon Merlo"
    assert data["nickname"] == "Lenon"
    assert data["whatsapp"] == "27997343401"
    assert data["gender"] == "M"
    assert data["type"] == "member"
    assert data["status"] == "pending"
    assert data["warnings"] == 0


def test_create_player_rejects_duplicate_whatsapp() -> None:
    payload = {
        "name": "Lenon Merlo",
        "nickname": "Lenon",
        "whatsapp": "27997343401",
        "gender": "M",
    }

    first_response = client.post("/api/v1/players", json=payload)
    second_response = client.post("/api/v1/players", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Este WhatsApp já está cadastrado."
    }


def test_get_player_returns_created_player() -> None:
    create_response = client.post(
        "/api/v1/players",
        json={
            "name": "Greici",
            "nickname": None,
            "whatsapp": "27999519575",
            "gender": "F",
        },
    )
    player_id = create_response.json()["id"]

    response = client.get(f"/api/v1/players/{player_id}")

    assert response.status_code == 200
    assert response.json()["id"] == player_id
    assert response.json()["name"] == "Greici"


def test_get_player_returns_404_when_missing() -> None:
    response = client.get("/api/v1/players/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found."}


def test_games_module_is_registered() -> None:
    response = client.get("/api/v1/games")

    assert response.status_code == 200
    assert response.json() == []

def test_create_game_returns_created_game() -> None:
    response = client.post(
        "/api/v1/games",
        json={
            "date": "2026-07-05",
            "location": "Arena Conecta",
            "time": "08:00:00",
            "status": "active",
            "notes": "Jogo oficial de domingo",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == "sunday-2026-07-05"
    assert data["day"] == "sunday"
    assert data["date"] == "2026-07-05"
    assert data["location"] == "Arena Conecta"
    assert data["time"] == "08:00:00"
    assert data["status"] == "active"
    assert data["notes"] == "Jogo oficial de domingo"


def test_create_game_rejects_non_wednesday_or_sunday() -> None:
    response = client.post(
        "/api/v1/games",
        json={
            "date": "2026-07-06",
            "location": "Arena Conecta",
            "time": "19:00:00",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Games must be scheduled on Wednesday or Sunday."
    }


def test_create_game_rejects_duplicate_date() -> None:
    payload = {
        "date": "2026-07-05",
        "location": "Arena Conecta",
        "time": "08:00:00",
    }

    first_response = client.post("/api/v1/games", json=payload)
    second_response = client.post("/api/v1/games", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Este jogo já está cadastrado."}


def test_get_game_returns_created_game() -> None:
    create_response = client.post(
        "/api/v1/games",
        json={
            "date": "2026-07-08",
            "location": "Arena Conecta",
            "time": "19:30:00",
        },
    )
    game_id = create_response.json()["id"]

    response = client.get(f"/api/v1/games/{game_id}")

    assert response.status_code == 200
    assert response.json()["id"] == game_id
    assert response.json()["day"] == "wednesday"


def test_get_game_returns_404_when_missing() -> None:
    response = client.get("/api/v1/games/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found."}


def test_update_game_returns_updated_game() -> None:
    create_response = client.post(
        "/api/v1/games",
        json={
            "date": "2026-07-05",
            "location": "Arena Conecta",
            "time": "08:00:00",
        },
    )
    game_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/games/{game_id}",
        json={
            "location": "Quadra Central",
            "time": "09:00:00",
            "notes": "Horario atualizado",
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == game_id
    assert response.json()["location"] == "Quadra Central"
    assert response.json()["time"] == "09:00:00"
    assert response.json()["notes"] == "Horario atualizado"


def test_update_game_can_change_id_when_date_changes() -> None:
    create_response = client.post(
        "/api/v1/games",
        json={
            "date": "2026-07-05",
            "location": "Arena Conecta",
            "time": "08:00:00",
        },
    )
    game_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/games/{game_id}",
        json={"date": "2026-07-12"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == "sunday-2026-07-12"
    assert client.get(f"/api/v1/games/{game_id}").status_code == 404


def test_update_game_returns_404_when_missing() -> None:
    response = client.patch(
        "/api/v1/games/missing",
        json={"location": "Quadra Central"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found."}


def test_delete_game_removes_game() -> None:
    create_response = client.post(
        "/api/v1/games",
        json={
            "date": "2026-07-05",
            "location": "Arena Conecta",
            "time": "08:00:00",
        },
    )
    game_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/games/{game_id}")
    get_response = client.get(f"/api/v1/games/{game_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_delete_game_returns_404_when_missing() -> None:
    response = client.delete("/api/v1/games/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found."}

def test_registrations_module_is_registered() -> None:
    response = client.get("/api/v1/registrations")

    assert response.status_code == 200
    assert response.json() == []


def test_teams_module_is_registered() -> None:
    response = client.get("/api/v1/teams")

    assert response.status_code == 200
    assert response.json() == []

def test_update_player_returns_updated_player() -> None:
    create_response = client.post(
        "/api/v1/players",
        json={
            "name": "Lenon Merlo",
            "nickname": "Lenon",
            "whatsapp": "27997343401",
            "gender": "M",
        },
    )
    player_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/players/{player_id}",
        json={
            "nickname": "Lennon",
            "warnings": 2,
            "status": "penalized",
        },
    )


    assert response.status_code == 200
    assert response.json()["id"] == player_id
    assert response.json()["nickname"] == "Lennon"
    assert response.json()["warnings"] == 2
    assert response.json()["status"] == "penalized"


def test_update_player_rejects_duplicate_whatsapp() -> None:
    first_response = client.post(
        "/api/v1/players",
        json={
            "name": "Lenon Merlo",
            "nickname": "Lenon",
            "whatsapp": "27997343401",
            "gender": "M",
        },
    )
    second_response = client.post(
        "/api/v1/players",
        json={
            "name": "Greici",
            "nickname": None,
            "whatsapp": "27999519575",
            "gender": "F",
        },
    )

    response = client.patch(
        f"/api/v1/players/{second_response.json()['id']}",
        json={"whatsapp": first_response.json()["whatsapp"]},
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Este WhatsApp já está cadastrado."
    }


def test_update_player_returns_404_when_missing() -> None:
    response = client.patch(
        "/api/v1/players/missing",
        json={"nickname": "Missing"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found."}


def test_delete_player_removes_player() -> None:
    create_response = client.post(
        "/api/v1/players",
        json={
            "name": "Lenon Merlo",
            "nickname": "Lenon",
            "whatsapp": "27997343401",
            "gender": "M",
        },
    )
    player_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/players/{player_id}")
    get_response = client.get(f"/api/v1/players/{player_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_delete_player_returns_404_when_missing() -> None:
    response = client.delete("/api/v1/players/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found."}