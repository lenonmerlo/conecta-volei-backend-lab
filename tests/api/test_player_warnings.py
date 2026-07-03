from tests.api.conftest import assert_error_response


def test_add_warning_keeps_player_active_on_first_warning(
    client,
    create_test_player,
) -> None:
    player = create_test_player("27991111111")

    response = client.post(f"/api/v1/players/{player['id']}/warnings")

    assert response.status_code == 200
    assert response.json()["warnings"] == 1
    assert response.json()["status"] == "active"


def test_add_second_warning_penalizes_player(
    client,
    create_test_player,
) -> None:
    player = create_test_player("27992222222")

    client.post(f"/api/v1/players/{player['id']}/warnings")
    response = client.post(f"/api/v1/players/{player['id']}/warnings")

    assert response.status_code == 200
    assert response.json()["warnings"] == 2
    assert response.json()["status"] == "penalized"


def test_add_third_warning_blocks_player(
    client,
    create_test_player,
) -> None:
    player = create_test_player("27993333333")

    client.post(f"/api/v1/players/{player['id']}/warnings")
    client.post(f"/api/v1/players/{player['id']}/warnings")
    response = client.post(f"/api/v1/players/{player['id']}/warnings")

    assert response.status_code == 200
    assert response.json()["warnings"] == 3
    assert response.json()["status"] == "blocked"


def test_remove_warning_recalculates_player_status(
    client,
    create_test_player,
) -> None:
    player = create_test_player("27994444444")

    client.post(f"/api/v1/players/{player['id']}/warnings")
    client.post(f"/api/v1/players/{player['id']}/warnings")

    response = client.delete(f"/api/v1/players/{player['id']}/warnings")

    assert response.status_code == 200
    assert response.json()["warnings"] == 1
    assert response.json()["status"] == "active"


def test_reset_warnings_sets_player_back_to_active(
    client,
    create_test_player,
) -> None:
    player = create_test_player("27995555555")

    client.post(f"/api/v1/players/{player['id']}/warnings")
    client.post(f"/api/v1/players/{player['id']}/warnings")
    client.post(f"/api/v1/players/{player['id']}/warnings")

    response = client.post(f"/api/v1/players/{player['id']}/warnings/reset")

    assert response.status_code == 200
    assert response.json()["warnings"] == 0
    assert response.json()["status"] == "active"


def test_player_with_two_warnings_joins_waitlist(
    client,
    create_test_player,
    create_test_game,
) -> None:
    player = create_test_player("27996666666")
    game = create_test_game()

    client.post(f"/api/v1/players/{player['id']}/warnings")
    client.post(f"/api/v1/players/{player['id']}/warnings")

    response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
            "invited_by": None,
        },
    )

    assert response.status_code == 201
    assert response.json()["slot"] == "waitlist"


def test_player_with_three_warnings_cannot_join_game(
    client,
    create_test_player,
    create_test_game,
) -> None:
    player = create_test_player("27997777777")
    game = create_test_game()

    client.post(f"/api/v1/players/{player['id']}/warnings")
    client.post(f"/api/v1/players/{player['id']}/warnings")
    client.post(f"/api/v1/players/{player['id']}/warnings")

    response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
            "invited_by": None,
        },
    )

    assert_error_response(
        response,
        status_code=403,
        message="Blocked players cannot join games.",
    )


def test_add_warning_returns_not_found_for_missing_player(client) -> None:
    response = client.post("/api/v1/players/missing-player/warnings")

    assert_error_response(
        response,
        status_code=404,
        message="Player not found.",
    )


def test_remove_warning_returns_not_found_for_missing_player(client) -> None:
    response = client.delete("/api/v1/players/missing-player/warnings")

    assert_error_response(
        response,
        status_code=404,
        message="Player not found.",
    )


def test_reset_warnings_returns_not_found_for_missing_player(client) -> None:
    response = client.post("/api/v1/players/missing-player/warnings/reset")

    assert_error_response(
        response,
        status_code=404,
        message="Player not found.",
    )