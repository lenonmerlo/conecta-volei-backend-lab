from fastapi.testclient import TestClient


def test_create_game_returns_created_game(client: TestClient) -> None:
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


def test_create_game_rejects_non_wednesday_or_sunday(
    client: TestClient,
) -> None:
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


def test_create_game_rejects_duplicate_date(client: TestClient) -> None:
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


def test_get_game_returns_created_game(client: TestClient) -> None:
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


def test_get_game_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/api/v1/games/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found."}


def test_update_game_returns_updated_game(client: TestClient) -> None:
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


def test_update_game_can_change_id_when_date_changes(
    client: TestClient,
) -> None:
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


def test_update_game_returns_404_when_missing(client: TestClient) -> None:
    response = client.patch(
        "/api/v1/games/missing",
        json={"location": "Quadra Central"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found."}


def test_delete_game_removes_game(client: TestClient) -> None:
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


def test_delete_game_returns_404_when_missing(client: TestClient) -> None:
    response = client.delete("/api/v1/games/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found."}