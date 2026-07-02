from collections.abc import Callable

from fastapi.testclient import TestClient


def test_join_game_adds_player_to_main_list(
    client: TestClient,
    create_test_player: Callable[..., dict],
    create_test_game: Callable[[], dict],
) -> None:
    player = create_test_player("27990000001", status="active")
    game = create_test_game()

    response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["game_id"] == game["id"]
    assert response.json()["player_id"] == player["id"]
    assert response.json()["slot"] == "main"


def test_join_game_rejects_duplicate_player(
    client: TestClient,
    create_test_player: Callable[..., dict],
    create_test_game: Callable[[], dict],
) -> None:
    player = create_test_player("27990000002", status="active")
    game = create_test_game()
    payload = {
        "game_id": game["id"],
        "player_id": player["id"],
    }

    first_response = client.post("/api/v1/registrations/join", json=payload)
    second_response = client.post("/api/v1/registrations/join", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Player already registered for this game."
    }


def test_join_game_blocks_blocked_player(
    client: TestClient,
    create_test_player: Callable[..., dict],
    create_test_game: Callable[[], dict],
) -> None:
    player = create_test_player("27990000003", status="blocked")
    game = create_test_game()

    response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Blocked players cannot join games."}


def test_join_game_places_penalized_player_on_waitlist(
    client: TestClient,
    create_test_player: Callable[..., dict],
    create_test_game: Callable[[], dict],
) -> None:
    player = create_test_player("27990000004", status="penalized")
    game = create_test_game()

    response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["slot"] == "waitlist"


def test_join_game_places_player_on_waitlist_when_main_is_full(
    client: TestClient,
    create_test_player: Callable[..., dict],
    create_test_game: Callable[[], dict],
) -> None:
    game = create_test_game()

    for index in range(21):
        player = create_test_player(f"27991{index:06d}", status="active")
        response = client.post(
            "/api/v1/registrations/join",
            json={
                "game_id": game["id"],
                "player_id": player["id"],
            },
        )
        assert response.status_code == 201

    waitlist_player = create_test_player("27992000000", status="active")
    response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": waitlist_player["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["slot"] == "waitlist"


def test_list_registrations_filters_by_game_id(
    client: TestClient,
    create_test_player: Callable[..., dict],
    create_test_game: Callable[[], dict],
) -> None:
    player = create_test_player("27990000005", status="active")
    game = create_test_game()

    client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
        },
    )

    response = client.get(f"/api/v1/registrations?game_id={game['id']}")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["player_id"] == player["id"]


def test_leave_game_removes_registration(
    client: TestClient,
    create_test_player: Callable[..., dict],
    create_test_game: Callable[[], dict],
) -> None:
    player = create_test_player("27990000006", status="active")
    game = create_test_game()

    client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
        },
    )

    leave_response = client.post(
        "/api/v1/registrations/leave",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
        },
    )
    list_response = client.get(f"/api/v1/registrations?game_id={game['id']}")

    assert leave_response.status_code == 204
    assert list_response.json() == []


def test_leave_game_promotes_first_waitlist_player(
    client: TestClient,
    create_test_player: Callable[..., dict],
    create_test_game: Callable[[], dict],
) -> None:
    game = create_test_game()
    main_players = []

    for index in range(21):
        player = create_test_player(f"27993{index:06d}", status="active")
        main_players.append(player)
        client.post(
            "/api/v1/registrations/join",
            json={
                "game_id": game["id"],
                "player_id": player["id"],
            },
        )

    waitlist_player = create_test_player("27994000000", status="active")
    waitlist_response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": waitlist_player["id"],
        },
    )
    assert waitlist_response.json()["slot"] == "waitlist"

    client.post(
        "/api/v1/registrations/leave",
        json={
            "game_id": game["id"],
            "player_id": main_players[0]["id"],
        },
    )

    registrations_response = client.get(
        f"/api/v1/registrations?game_id={game['id']}"
    )

    promoted = [
        registration
        for registration in registrations_response.json()
        if registration["player_id"] == waitlist_player["id"]
    ][0]

    assert promoted["slot"] == "main"


def test_leave_game_returns_404_when_registration_is_missing(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/registrations/leave",
        json={
            "game_id": "missing-game",
            "player_id": "missing-player",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Registration not found."}