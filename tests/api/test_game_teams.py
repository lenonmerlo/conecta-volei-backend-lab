from fastapi.testclient import TestClient

from tests.api.conftest import assert_error_response


def make_team(name: str = "Time A") -> dict:
    return {
        "name": name,
        "players": [
            {
                "id": "p-1",
                "name": "Player 1",
                "skill_level": 5,
                "gender": "M",
                "is_captain": True,
                "is_setter": False,
                "position": "attacker",
            }
        ],
        "total_level": 5,
    }


def test_list_game_teams_returns_empty_list(
    client: TestClient,
    create_test_game,
) -> None:
    game = create_test_game()

    response = client.get(f"/api/v1/games/{game['id']}/teams")

    assert response.status_code == 200
    assert response.json() == []


def test_save_game_teams_replaces_existing_teams(
    client: TestClient,
    create_test_admin,
    create_test_game,
) -> None:
    admin = create_test_admin("27990300001")
    game = create_test_game()

    first_response = client.put(
        f"/api/v1/games/{game['id']}/teams",
        headers=admin["headers"],
        json={
            "teams": [
                make_team("Time A"),
                make_team("Time B"),
            ],
        },
    )

    assert first_response.status_code == 200
    assert len(first_response.json()) == 2

    second_response = client.put(
        f"/api/v1/games/{game['id']}/teams",
        headers=admin["headers"],
        json={
            "teams": [
                make_team("Time C"),
            ],
        },
    )

    assert second_response.status_code == 200
    assert len(second_response.json()) == 1
    assert second_response.json()[0]["name"] == "Time C"

    list_response = client.get(f"/api/v1/games/{game['id']}/teams")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["name"] == "Time C"


def test_save_game_teams_requires_admin(
    client: TestClient,
    create_test_game,
) -> None:
    game = create_test_game()

    response = client.put(
        f"/api/v1/games/{game['id']}/teams",
        json={"teams": [make_team()]},
    )

    assert_error_response(
        response,
        status_code=401,
        message="Invalid authentication credentials.",
    )


def test_list_game_teams_returns_not_found_for_missing_game(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/games/missing-game/teams")

    assert_error_response(
        response,
        status_code=404,
        message="Game not found.",
    )


def test_save_game_teams_returns_not_found_for_missing_game(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990300002")

    response = client.put(
        "/api/v1/games/missing-game/teams",
        headers=admin["headers"],
        json={"teams": [make_team()]},
    )

    assert_error_response(
        response,
        status_code=404,
        message="Game not found.",
    )