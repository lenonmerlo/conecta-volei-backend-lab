from app.domain.team_draw import DrawPlayer, DrawTeam, draw_teams, swap_players


def make_player(index: int, **overrides: object) -> DrawPlayer:
    data = {
        "id": f"p-{index}",
        "name": f"Player {index}",
        "skill_level": 3,
        "gender": "M",
        "is_captain": False,
        "is_setter": False,
        "position": "middle",
    }
    data.update(overrides)
    return DrawPlayer(**data)


def test_draw_teams_with_21_players_generates_three_teams_of_seven() -> None:
    players = [make_player(index) for index in range(1, 22)]

    teams = draw_teams(players)

    assert len(teams) == 3
    assert all(len(team.players) == 7 for team in teams)


def test_draw_teams_with_10_players_generates_two_teams_of_five() -> None:
    players = [make_player(index) for index in range(1, 11)]

    teams = draw_teams(players)

    assert len(teams) == 2
    assert all(len(team.players) == 5 for team in teams)


def test_draw_teams_with_7_players_returns_empty_list() -> None:
    players = [make_player(index) for index in range(1, 8)]

    teams = draw_teams(players)

    assert teams == []


def test_draw_teams_distributes_captains_between_teams() -> None:
    players = [
        make_player(index, is_captain=index in {1, 2, 3})
        for index in range(1, 22)
    ]

    teams = draw_teams(players)

    captain_counts = [
        sum(1 for player in team.players if player.is_captain)
        for team in teams
    ]

    assert captain_counts == [1, 1, 1]


def test_draw_teams_balances_female_players() -> None:
    players = [
        make_player(
            index,
            gender="F" if index in {1, 2, 3} else "M",
            is_captain=index in {1, 2, 3},
        )
        for index in range(1, 22)
    ]

    teams = draw_teams(players)

    female_counts = [
        sum(1 for player in team.players if player.gender == "F")
        for team in teams
    ]

    assert female_counts == [1, 1, 1]


def test_swap_players_between_teams() -> None:
    teams = [
        DrawTeam(
            name="Time A",
            players=[
                make_player(1, skill_level=1),
                make_player(2, skill_level=2),
            ],
        ),
        DrawTeam(
            name="Time B",
            players=[
                make_player(3, skill_level=3),
                make_player(4, skill_level=4),
            ],
        ),
    ]

    swapped = swap_players(teams, 0, "p-1", 1, "p-3")

    assert [player.id for player in swapped[0].players] == ["p-3", "p-2"]
    assert [player.id for player in swapped[1].players] == ["p-1", "p-4"]
    assert swapped[0].total_level == 5
    assert swapped[1].total_level == 5


def test_swap_players_returns_original_when_player_is_missing() -> None:
    teams = [
        DrawTeam(name="Time A", players=[make_player(1)]),
        DrawTeam(name="Time B", players=[make_player(2)]),
    ]

    swapped = swap_players(teams, 0, "missing", 1, "p-2")

    assert swapped is teams