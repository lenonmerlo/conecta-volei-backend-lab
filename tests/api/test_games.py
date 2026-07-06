from fastapi.testclient import TestClient

from tests.api.conftest import assert_error_response


def test_create_game_returns_created_game(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990100001")

    response = client.post(
        "/api/v1/games",
        headers=admin["headers"],
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
    create_test_admin,
) -> None:
    admin = create_test_admin("27990100002")

    response = client.post(
        "/api/v1/games",
        headers=admin["headers"],
        json={
            "date": "2026-07-06",
            "location": "Arena Conecta",
            "time": "19:00:00",
        },
    )

    assert_error_response(
        response,
        status_code=409,
        message="Games must be scheduled on Wednesday or Sunday.",
    )


def test_create_game_rejects_duplicate_date(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990100003")
    payload = {
        "date": "2026-07-05",
        "location": "Arena Conecta",
        "time": "08:00:00",
    }

    first_response = client.post(
        "/api/v1/games",
        headers=admin["headers"],
        json=payload,
    )
    second_response = client.post(
        "/api/v1/games",
        headers=admin["headers"],
        json=payload,
    )

    assert first_response.status_code == 201
    assert_error_response(
        second_response,
        status_code=409,
        message="Este jogo já está cadastrado.",
    )


def test_get_game_returns_created_game(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990100004")

    create_response = client.post(
        "/api/v1/games",
        headers=admin["headers"],
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

    assert_error_response(
        response,
        status_code=404,
        message="Game not found.",
    )


def test_update_game_returns_updated_game(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990100005")

    create_response = client.post(
        "/api/v1/games",
        headers=admin["headers"],
        json={
            "date": "2026-07-05",
            "location": "Arena Conecta",
            "time": "08:00:00",
        },
    )
    game_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/games/{game_id}",
        headers=admin["headers"],
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
    create_test_admin,
) -> None:
    admin = create_test_admin("27990100006")

    create_response = client.post(
        "/api/v1/games",
        headers=admin["headers"],
        json={
            "date": "2026-07-05",
            "location": "Arena Conecta",
            "time": "08:00:00",
        },
    )
    game_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/games/{game_id}",
        headers=admin["headers"],
        json={"date": "2026-07-12"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == "sunday-2026-07-12"
    assert client.get(f"/api/v1/games/{game_id}").status_code == 404


def test_update_game_returns_404_when_missing(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990100007")

    response = client.patch(
        "/api/v1/games/missing",
        headers=admin["headers"],
        json={"location": "Quadra Central"},
    )

    assert_error_response(
        response,
        status_code=404,
        message="Game not found.",
    )


def test_delete_game_removes_game(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990100008")

    create_response = client.post(
        "/api/v1/games",
        headers=admin["headers"],
        json={
            "date": "2026-07-05",
            "location": "Arena Conecta",
            "time": "08:00:00",
        },
    )
    game_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/games/{game_id}",
        headers=admin["headers"],
    )
    get_response = client.get(f"/api/v1/games/{game_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_delete_game_returns_404_when_missing(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990100009")

    response = client.delete(
        "/api/v1/games/missing",
        headers=admin["headers"],
    )

    assert_error_response(
        response,
        status_code=404,
        message="Game not found.",
    )


def test_create_game_requires_admin(client: TestClient) -> None:
    response = client.post(
        "/api/v1/games",
        json={
            "date": "2026-07-05",
            "location": "Arena Conecta",
            "time": "08:00:00",
        },
    )

    assert_error_response(
        response,
        status_code=401,
        message="Invalid authentication credentials.",
    )