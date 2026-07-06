from datetime import UTC, datetime

from app.modules.audit_logs.repository import AuditLogRepository
from app.modules.audit_logs.schemas import AuditLogCreate
from app.modules.audit_logs.service import create_audit_log, list_audit_logs
from tests.conftest import TestSessionLocal


def test_create_audit_log_persists_log() -> None:
    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)

        audit_log = create_audit_log(
            repository,
            AuditLogCreate(
                action="player.created",
                details={"status": "pending"},
            ),
        )

        assert audit_log.id
        assert audit_log.action == "player.created"
        assert audit_log.details == {"status": "pending"}


def test_list_audit_logs_returns_latest_first() -> None:
    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)

        first_log = create_audit_log(
            repository,
            AuditLogCreate(action="player.created"),
        )
        second_log = create_audit_log(
            repository,
            AuditLogCreate(action="registration.joined"),
        )

        audit_logs = list_audit_logs(repository)

        assert [audit_log.id for audit_log in audit_logs[:2]] == [
            second_log.id,
            first_log.id,
        ]

def test_create_player_writes_audit_log(client) -> None:
    response = client.post(
        "/api/v1/players",
        json={
            "name": "Audit Player",
            "nickname": None,
            "whatsapp": "27990001000",
            "gender": "M",
        },
    )

    assert response.status_code == 201

    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)
        audit_logs = list_audit_logs(repository)

    assert audit_logs[0].action == "player.created"
    assert audit_logs[0].target_player_id == response.json()["id"]
    assert audit_logs[0].details == {
        "status": "pending",
        "type": "member",
        "role": "player",
    }

def test_join_game_writes_audit_log(
    client,
    create_test_game,
    create_test_player,
) -> None:
    game = create_test_game()
    player = create_test_player("27990002000")

    response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
            "invited_by": None,
        },
    )

    assert response.status_code == 201

    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)
        audit_logs = list_audit_logs(repository)

    assert audit_logs[0].action == "registration.joined"
    assert audit_logs[0].target_player_id == player["id"]
    assert audit_logs[0].game_id == game["id"]
    assert audit_logs[0].details == {
        "registration_id": response.json()["id"],
        "slot": "main",
        "invited_by": None,
    }

def test_leave_game_writes_audit_log(
    client,
    create_test_game,
    create_test_player,
) -> None:
    game = create_test_game()
    player = create_test_player("27990003000")

    join_response = client.post(
        "/api/v1/registrations/join",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
            "invited_by": None,
        },
    )

    assert join_response.status_code == 201

    leave_response = client.post(
        "/api/v1/registrations/leave",
        json={
            "game_id": game["id"],
            "player_id": player["id"],
        },
    )

    assert leave_response.status_code == 204

    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)
        audit_logs = list_audit_logs(repository)

    assert audit_logs[0].action == "registration.left"
    assert audit_logs[0].actor_player_id == player["id"]
    assert audit_logs[0].target_player_id == player["id"]
    assert audit_logs[0].game_id == game["id"]
    assert audit_logs[0].details == {
        "registration_id": join_response.json()["id"],
        "slot": "main",
    }

def test_add_warning_writes_audit_log(
    client,
    create_test_admin,
    create_test_player,
) -> None:
    admin = create_test_admin("27990004000")
    player = create_test_player("27990004001")

    response = client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )

    assert response.status_code == 200

    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)
        audit_logs = list_audit_logs(repository)

    assert audit_logs[0].action == "player.warning_added"
    assert audit_logs[0].actor_player_id == admin["id"]
    assert audit_logs[0].target_player_id == player["id"]
    assert audit_logs[0].details == {
        "previous_warnings": 0,
        "new_warnings": 1,
        "previous_status": "active",
        "new_status": "active",
    }


def test_second_warning_writes_penalized_audit_log(
    client,
    create_test_admin,
    create_test_player,
) -> None:
    admin = create_test_admin("27990005000")
    player = create_test_player("27990005001")

    client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )
    response = client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )

    assert response.status_code == 200
    assert response.json()["status"] == "penalized"

    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)
        audit_logs = list_audit_logs(repository)

    assert audit_logs[0].action == "player.penalized"
    assert audit_logs[0].actor_player_id == admin["id"]
    assert audit_logs[0].target_player_id == player["id"]
    assert audit_logs[0].details == {
        "warnings": 2,
        "previous_status": "active",
        "new_status": "penalized",
    }


def test_third_warning_writes_blocked_audit_log(
    client,
    create_test_admin,
    create_test_player,
) -> None:
    admin = create_test_admin("27990006000")
    player = create_test_player("27990006001")

    client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )
    client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )
    response = client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )

    assert response.status_code == 200
    assert response.json()["status"] == "blocked"

    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)
        audit_logs = list_audit_logs(repository)

    assert audit_logs[0].action == "player.blocked"
    assert audit_logs[0].actor_player_id == admin["id"]
    assert audit_logs[0].target_player_id == player["id"]
    assert audit_logs[0].details == {
        "warnings": 3,
        "previous_status": "penalized",
        "new_status": "blocked",
    }

def test_remove_warning_writes_audit_log(
    client,
    create_test_admin,
    create_test_player,
) -> None:
    admin = create_test_admin("27990007000")
    player = create_test_player("27990007001")

    client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )
    client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )

    response = client.delete(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )

    assert response.status_code == 200

    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)
        audit_logs = list_audit_logs(repository)

    assert audit_logs[0].action == "player.warning_removed"
    assert audit_logs[0].actor_player_id == admin["id"]
    assert audit_logs[0].target_player_id == player["id"]
    assert audit_logs[0].details == {
        "previous_warnings": 2,
        "new_warnings": 1,
        "previous_status": "penalized",
        "new_status": "active",
    }


def test_reset_warnings_writes_audit_log(
    client,
    create_test_admin,
    create_test_player,
) -> None:
    admin = create_test_admin("27990008000")
    player = create_test_player("27990008001")

    client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )
    client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )
    client.post(
        f"/api/v1/players/{player['id']}/warnings",
        headers=admin["headers"],
    )

    response = client.post(
        f"/api/v1/players/{player['id']}/warnings/reset",
        headers=admin["headers"],
    )

    assert response.status_code == 200

    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)
        audit_logs = list_audit_logs(repository)

    assert audit_logs[0].action == "player.warnings_reset"
    assert audit_logs[0].actor_player_id == admin["id"]
    assert audit_logs[0].target_player_id == player["id"]
    assert audit_logs[0].details == {
        "previous_warnings": 3,
        "new_warnings": 0,
        "previous_status": "blocked",
        "new_status": "active",
    }

def test_process_guest_registrations_writes_audit_log(
    client,
    create_test_admin,
    create_test_game,
    create_test_player,
    monkeypatch,
) -> None:
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 7, 3, 12, 0, tzinfo=UTC)

    monkeypatch.setattr(
        "app.modules.registrations.service.datetime",
        FixedDatetime,
    )

    admin = create_test_admin("27990009000")
    game = create_test_game()
    invited_by = create_test_player(
        "27990009001",
        name="Member Player",
    )
    guest = create_test_player(
        "27990009002",
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
        headers=admin["headers"],
    )

    assert response.status_code == 200

    with TestSessionLocal() as session:
        repository = AuditLogRepository(session)
        audit_logs = list_audit_logs(repository)

    assert audit_logs[0].action == "guest_registration.processed"
    assert audit_logs[0].actor_player_id == admin["id"]
    assert audit_logs[0].target_player_id == guest["id"]
    assert audit_logs[0].game_id == game["id"]
    assert audit_logs[0].details == {
        "registration_id": join_response.json()["id"],
        "new_slot": "main",
        "invited_by": invited_by["id"],
    }