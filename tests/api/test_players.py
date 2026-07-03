from fastapi.testclient import TestClient

from tests.api.conftest import assert_error_response


def test_create_player_returns_created_player(client: TestClient) -> None:
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


def test_create_player_rejects_duplicate_whatsapp(client: TestClient) -> None:
    payload = {
        "name": "Lenon Merlo",
        "nickname": "Lenon",
        "whatsapp": "27997343401",
        "gender": "M",
    }

    first_response = client.post("/api/v1/players", json=payload)
    second_response = client.post("/api/v1/players", json=payload)

    assert first_response.status_code == 201
    assert_error_response(
        second_response,
        status_code=409,
        message="Este WhatsApp já está cadastrado.",
    )


def test_get_player_returns_created_player(client: TestClient) -> None:
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


def test_get_player_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/api/v1/players/missing")

    assert_error_response(
        response,
        status_code=404,
        message="Player not found.",
    )


def test_update_player_returns_updated_player(client: TestClient) -> None:
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


def test_update_player_rejects_duplicate_whatsapp(client: TestClient) -> None:
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

    assert_error_response(
        response,
        status_code=409,
        message="Este WhatsApp já está cadastrado.",
    )


def test_update_player_returns_404_when_missing(client: TestClient) -> None:
    response = client.patch(
        "/api/v1/players/missing",
        json={"nickname": "Missing"},
    )

    assert_error_response(
        response,
        status_code=404,
        message="Player not found.",
    )


def test_delete_player_removes_player(client: TestClient) -> None:
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


def test_delete_player_returns_404_when_missing(client: TestClient) -> None:
    response = client.delete("/api/v1/players/missing")

    assert_error_response(
        response,
        status_code=404,
        message="Player not found.",
    )


def test_create_guest_player(client) -> None:
    response = client.post(
        "/api/v1/players",
        json={
            "name": "Guest Player",
            "nickname": None,
            "whatsapp": "27997349999",
            "gender": "M",
            "type": "guest",
        },
    )

    assert response.status_code == 201
    assert response.json()["type"] == "guest"


def test_update_player_type(client, create_test_player) -> None:
    player = create_test_player("27997348888")

    response = client.patch(
        f"/api/v1/players/{player['id']}",
        json={"type": "guest"},
    )

    assert response.status_code == 200
    assert response.json()["type"] == "guest"