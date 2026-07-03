def test_process_guest_registrations_endpoint_returns_empty_list_for_unknown_game(
    client,
) -> None:
    response = client.post(
        "/api/v1/registrations/process-guests",
        params={"game_id": "missing-game"},
    )

    assert response.status_code == 200
    assert response.json() == []