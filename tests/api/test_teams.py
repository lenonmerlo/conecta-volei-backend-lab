from fastapi.testclient import TestClient

from tests.api.conftest import assert_error_response


def make_player(index: int, **overrides: object) -> dict:
    player = {
        "id": f"p-{index}",
        "name": f"Player {index}",
        "skill_level": 3,
        "gender": "M",
        "is_captain": False,
        "is_setter": False,
        "position": "middle",
    }
    player.update(overrides)
    return player


def test_list_teams_returns_empty_list(client: TestClient) -> None:
    response = client.get("/api/v1/teams")

    assert response.status_code == 200
    assert response.json() == []


def test_draw_teams_returns_balanced_groups(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990200001")
    players = [make_player(index) for index in range(1, 11)]

    response = client.post(
        "/api/v1/teams/draw",
        headers=admin["headers"],
        json={"players": players},
    )

    assert response.status_code == 200

    teams = response.json()
    assert len(teams) == 2
    assert [team["name"] for team in teams] == ["Time A", "Time B"]
    assert all(len(team["players"]) == 5 for team in teams)
    assert all("total_level" in team for team in teams)


def test_draw_teams_returns_empty_list_when_not_enough_players(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990200002")
    players = [make_player(index) for index in range(1, 8)]

    response = client.post(
        "/api/v1/teams/draw",
        headers=admin["headers"],
        json={"players": players},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_draw_teams_requires_admin(client: TestClient) -> None:
    players = [make_player(index) for index in range(1, 11)]

    response = client.post(
        "/api/v1/teams/draw",
        json={"players": players},
    )

    assert_error_response(
        response,
        status_code=401,
        message="Invalid authentication credentials.",
    )


def test_swap_teams_returns_swapped_players(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990200003")

    response = client.post(
        "/api/v1/teams/swap",
        headers=admin["headers"],
        json={
            "teams": [
                {
                    "name": "Time A",
                    "players": [
                        make_player(1, skill_level=5),
                        make_player(2, skill_level=3),
                    ],
                },
                {
                    "name": "Time B",
                    "players": [
                        make_player(3, skill_level=2),
                        make_player(4, skill_level=4),
                    ],
                },
            ],
            "from_team_index": 0,
            "from_player_id": "p-1",
            "to_team_index": 1,
            "to_player_id": "p-3",
        },
    )

    assert response.status_code == 200

    teams = response.json()
    assert teams[0]["players"][0]["id"] == "p-3"
    assert teams[1]["players"][0]["id"] == "p-1"
    assert teams[0]["total_level"] == 5
    assert teams[1]["total_level"] == 9


def test_swap_teams_returns_original_when_player_is_missing(
    client: TestClient,
    create_test_admin,
) -> None:
    admin = create_test_admin("27990200004")

    response = client.post(
        "/api/v1/teams/swap",
        headers=admin["headers"],
        json={
            "teams": [
                {
                    "name": "Time A",
                    "players": [make_player(1)],
                },
                {
                    "name": "Time B",
                    "players": [make_player(2)],
                },
            ],
            "from_team_index": 0,
            "from_player_id": "missing-player",
            "to_team_index": 1,
            "to_player_id": "p-2",
        },
    )

    assert response.status_code == 200

    teams = response.json()
    assert teams[0]["players"][0]["id"] == "p-1"
    assert teams[1]["players"][0]["id"] == "p-2"


def test_swap_teams_requires_admin(client: TestClient) -> None:
    response = client.post(
        "/api/v1/teams/swap",
        json={
            "teams": [
                {
                    "name": "Time A",
                    "players": [make_player(1)],
                },
                {
                    "name": "Time B",
                    "players": [make_player(2)],
                },
            ],
            "from_team_index": 0,
            "from_player_id": "p-1",
            "to_team_index": 1,
            "to_player_id": "p-2",
        },
    )

    assert_error_response(
        response,
        status_code=401,
        message="Invalid authentication credentials.",
    )