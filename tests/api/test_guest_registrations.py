def test_guest_registration_goes_to_guests_slot_from_api(
    client,
    create_test_game,
    create_test_player,
) -> None:
    game = create_test_game()
    invited_by = create_test_player(
        "27997343401",
        name="Member Player",
    )
    guest = create_test_player(
        "27997343402",
        name="Guest Player",
        player_type="guest",
    )

    response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": guest["id"],
            "invited_by": invited_by["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["slot"] == "guests"


def test_process_guest_registrations_promotes_guest_to_main_from_api(
    client,
    create_test_game,
    create_test_player,
) -> None:
    game = create_test_game()
    invited_by = create_test_player(
        "27997343403",
        name="Member Player",
    )
    guest = create_test_player(
        "27997343404",
        name="Guest Player",
        player_type="guest",
    )

    join_response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": guest["id"],
            "invited_by": invited_by["id"],
        },
    )

    assert join_response.status_code == 201
    assert join_response.json()["slot"] == "guests"

    response = client.post(
        "/api/v1/registrations/process-guests",
        params={"game_id": game["id"]},
    )

    assert response.status_code == 200
    assert response.json()[0]["slot"] == "main"