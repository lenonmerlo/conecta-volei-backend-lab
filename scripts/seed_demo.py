from datetime import UTC, datetime

from app.core.database import SessionLocal
from app.domain.constants import PlayerStatus, PlayerType
from app.modules.games.repository import GameRepository
from app.modules.games.schemas import GameCreate
from app.modules.games.service import create_game, get_game
from app.modules.players.repository import PlayerRepository
from app.modules.players.schemas import PlayerCreate, PlayerUpdate
from app.modules.players.service import (
    add_warning,
    create_player,
    get_player_by_whatsapp,
    update_player,
)
from app.modules.registrations.repository import RegistrationRepository
from app.modules.registrations.schemas import RegistrationJoin
from app.modules.registrations.service import join_game

DEMO_GAME_DATE = "2026-07-05"
DEMO_GAME_ID = "sunday-2026-07-05"

def _get_or_create_game(game_repository: GameRepository):
    existing_game = get_game(game_repository, DEMO_GAME_ID)
    if existing_game:
        return existing_game

    return create_game(
        game_repository,
        GameCreate(
            date=DEMO_GAME_DATE,
            location="Arena Conecta Demo",
            time="08:00:00",
        ),
    )

def _get_or_create_player(
        player_repository: PlayerRepository,
        *,
        name: str,
        whatsapp: str,
        player_type: PlayerType = PlayerType.MEMBER,
        status: PlayerStatus = PlayerStatus.ACTIVE,
):
    existing_player = get_player_by_whatsapp(player_repository, whatsapp)
    if existing_player:
        return existing_player

    player = create_player(
        player_repository,
        PlayerCreate(
            name=name,
            nickname=None,
            whatsapp=whatsapp,
            gender="M",
            type=player_type,
        ),
    )

    return update_player(
        player_repository,
        player.id,
        PlayerUpdate(status=status),
    )

def _join_if_needed(
        registration_repository: RegistrationRepository,
        player_repository: PlayerRepository,
        game_repository: GameRepository,
        *,
        game_id: str,
        player_id: str,
        invited_by: str | None = None,
        now: datetime | None = None,
):
    existing_registration = registration_repository.get_player_registration(
        game_id,
        player_id,
    )
    if existing_registration:
        return existing_registration

    return join_game(
        RegistrationJoin(
            game_id=game_id,
            player_id=player_id,
            invited_by=invited_by,
        ),
        registration_repository,
        player_repository,
        game_repository,
        now=now,
    )

def run() -> None:
    with SessionLocal() as session:
        player_repository = PlayerRepository(session)
        game_repository = GameRepository(session)
        registration_repository = RegistrationRepository(session)

        game = _get_or_create_game(game_repository)

        members = []
        for index in range(21):
            member = _get_or_create_player(
                player_repository,
                name=f"Demo Member {index + 1:02d}",
                whatsapp=f"27991000{index:03d}",
            )
            members.append(member)

            _join_if_needed(
                registration_repository,
                player_repository,
                game_repository,
                game_id=game.id,
                player_id=member.id,
            )

        waitlist_player = _get_or_create_player(
            player_repository,
            name="Demo Waitlist Player",
            whatsapp="27992000001",
        )
        _join_if_needed(
            registration_repository,
            player_repository,
            game_repository,
            game_id=game.id,
            player_id=waitlist_player.id,
        )

        invited_by = members[0]
        guest = _get_or_create_player(
            player_repository,
            name="Demo Guest Player",
            whatsapp="27993000001",
            player_type=PlayerType.GUEST,
        )
        _join_if_needed(
            registration_repository,
            player_repository,
            game_repository,
            game_id=game.id,
            player_id=guest.id,
            invited_by=invited_by.id,
            now=datetime(2026, 7, 3, 12, 0, tzinfo=UTC),
        )

        penalized_player = _get_or_create_player(
            player_repository,
            name="Demo Penalized Player",
            whatsapp="27994000001",
        )
        add_warning(player_repository, penalized_player.id)
        add_warning(player_repository, penalized_player.id)

        blocked_player = _get_or_create_player(
            player_repository,
            name="Demo Blocked Player",
            whatsapp="27995000001",
        )
        add_warning(player_repository, blocked_player.id)
        add_warning(player_repository, blocked_player.id)
        add_warning(player_repository, blocked_player.id)

        print("Demo seed completed.")
        print(f"Game id: {game.id}")
        print("Expected slots:")
        print("- 21 players in main")
        print("- 1 players in waitlist")
        print("- 1 guest player in guests")
        print("- 1 penalized player")
        print("- 1 blocked player")

if __name__ == "__main__":
    run()

