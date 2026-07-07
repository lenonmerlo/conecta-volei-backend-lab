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
    assert response.json()["refresh_token"]
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


def test_login_returns_refresh_token_for_existing_player(
    client,
    create_test_player,
) -> None:
    player = create_test_player("27997343403")

    response = client.post(
        "/api/v1/auth/login",
        json={"whatsapp": player["whatsapp"]},
    )

    assert response.status_code == 200
    assert response.json()["refresh_token"]


def test_refresh_returns_new_access_token(
    client,
    create_test_player,
) -> None:
    player = create_test_player("27997343404")
    login_response = client.post(
        "/api/v1/auth/login",
        json={"whatsapp": player["whatsapp"]},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]
    assert response.json()["player"]["id"] == player["id"]


def test_refresh_returns_unauthorized_for_invalid_token(client) -> None:
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )

    assert_error_response(
        response,
        status_code=401,
        message="Invalid refresh token.",
    )


def test_me_rejects_refresh_token(
    client,
    create_test_player,
) -> None:
    player = create_test_player("27997343405")
    login_response = client.post(
        "/api/v1/auth/login",
        json={"whatsapp": player["whatsapp"]},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert_error_response(
        response,
        status_code=401,
        message="Invalid authentication credentials.",
    )