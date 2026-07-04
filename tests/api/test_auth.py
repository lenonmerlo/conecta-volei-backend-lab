from tests.api.conftest import assert_error_response


def test_login_returns_access_token_for_existing_player(
    client,
    create_test_player,
) -> None:
    player = create_test_player("27997343401")

    response = client.post(
        "/api/v1/auth/login",
        json={"whatsapp": player["whatsapp"]},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]
    assert response.json()["player"]["id"] == player["id"]


def test_login_returns_unauthorized_for_unknown_whatsapp(client) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"whatsapp": "27990000000"},
    )

    assert_error_response(
        response,
        status_code=401,
        message="Invalid credentials.",
    )


def test_me_returns_current_player(
    client,
    create_test_player,
) -> None:
    player = create_test_player("27997343402")
    login_response = client.post(
        "/api/v1/auth/login",
        json={"whatsapp": player["whatsapp"]},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == player["id"]


def test_me_returns_unauthorized_without_token(client) -> None:
    response = client.get("/api/v1/auth/me")

    assert_error_response(
        response,
        status_code=401,
        message="Invalid authentication credentials.",
    )